import React, { useEffect, useRef, useState } from 'react'
import { Html5QrcodeScanner, Html5QrcodeSupportedFormats, Html5QrcodeScanType } from 'html5-qrcode'
import axios from 'axios'
import { Button, Alert, Form, Spinner } from 'react-bootstrap'

interface ManualBarcodeProps {
  onProductFound: (brand: string, model: string) => void
}

const ManualBarcode: React.FC<ManualBarcodeProps> = ({ onProductFound }) => {
  const [error, setError] = useState<string | null>(null)
  const [scanning, setScanning] = useState(true)
  const [uploading, setUploading] = useState(false)
  const scannerRef = useRef<Html5QrcodeScanner | null>(null)

  // Remote logging helper to see logs in Portainer
  const remoteLog = (message: string, level: string = 'INFO', context: any = null) => {
    console.log(`[${level}] ${message}`, context || '');
    axios.post('/api/logs', {
      level,
      message,
      context: context ? JSON.stringify(context) : ''
    }).catch(err => console.error("Failed to send remote log:", err));
  }

  useEffect(() => {
    // Initialize scanner
    // Use a unique ID for the element
    const scannerId = "reader"
    
    // Cleanup previous instance if any (React strict mode double invoke)
    if (scannerRef.current) {
        scannerRef.current.clear().catch(console.error)
    }

    remoteLog("Initializing Html5QrcodeScanner", "INFO");

    const scanner = new Html5QrcodeScanner(
      scannerId,
      {
        fps: 20, // Increased FPS for smoother detection
        qrbox: (viewfinderWidth, viewfinderHeight) => {
            // Make it wider for 1D barcodes which are usually long and short
            const width = Math.min(viewfinderWidth * 0.8, 300);
            const height = Math.min(viewfinderHeight * 0.4, 200);
            return { width, height };
        },
        videoConstraints: {
            facingMode: "environment", // Use back camera
            width: { min: 640, ideal: 1280, max: 1920 }, // Request HD resolution
            height: { min: 480, ideal: 720, max: 1080 },
            // @ts-ignore - focusMode is non-standard but supported by some browsers
            focusMode: "continuous" 
        },
        experimentalFeatures: {
          useBarCodeDetectorIfSupported: false // Disable this as it can be flaky on some mobile browsers
        },
        supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA],
        formatsToSupport: [
          Html5QrcodeSupportedFormats.EAN_13,
          Html5QrcodeSupportedFormats.EAN_8,
          Html5QrcodeSupportedFormats.UPC_A,
          Html5QrcodeSupportedFormats.UPC_E,
          Html5QrcodeSupportedFormats.CODE_128,
          Html5QrcodeSupportedFormats.CODE_39,
          Html5QrcodeSupportedFormats.QR_CODE,
        ]
      },
      /* verbose= */ true
    )
    scannerRef.current = scanner

    remoteLog("Rendering scanner UI", "INFO");
    scanner.render(onScanSuccess, onScanFailure)

    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(console.error)
      }
    }
  }, [])

  const onScanSuccess = async (decodedText: string) => {
    remoteLog("Scanner detected barcode", "INFO", { barcode: decodedText });
    
    // Stop scanning
    if (scannerRef.current) {
        scannerRef.current.pause() 
    }
    setScanning(false)
    setError(null)

    try {
      const response = await axios.get('/api/products/lookup', {
        params: { barcode: decodedText }
      })
      const { brand, model } = response.data
      remoteLog("Barcode lookup success", "INFO", { barcode: decodedText, brand, model });
      
      // Pass to parent
      onProductFound(brand || '', model || '')
      
    } catch (err) {
      remoteLog("Barcode lookup failed", "WARNING", { barcode: decodedText, error: err });
      setError(`Product lookup failed for barcode: ${decodedText}. You may need to search manually.`)
    }
  }

  const onScanFailure = (errorMessage: any) => {
    // handle scan failure, usually better to ignore and keep scanning.
    // Filter out the common "No MultiFormat Readers" error to avoid console flood
    const errorStr = errorMessage?.toString() || '';
    if (errorStr.includes("No MultiFormat Readers")) {
        // Log every 50th failure to confirm life, otherwise silence
        // We can use a static counter or just random for simplicity since we don't have state here easily 
        // without triggering re-renders if we used state.
        if (Math.random() < 0.02) {
             remoteLog("Scanning active (looking for code...)", "DEBUG", { error: "No code detected" });
        }
        return;
    }
    // Only log significant errors to backend
    remoteLog("Scan failure event", "DEBUG", errorMessage);
  }
  
  const handleRestart = () => {
      remoteLog("Restarting scanner", "INFO");
      setScanning(true)
      setError(null)
      if (scannerRef.current) {
          scannerRef.current.resume()
      }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError(null)
    remoteLog("Starting file upload scan", "INFO", { fileName: file.name });

    const formData = new FormData()
    formData.append('file', file)

    try {
        // Safely pause scanner
        try {
            if (scannerRef.current && scanning) {
                scannerRef.current.pause()
            }
        } catch (pauseErr) {
            console.warn("Failed to pause scanner (non-fatal):", pauseErr)
        }

      const response = await axios.post('/api/products/scan-barcode', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000 // 30 seconds timeout
      })
      
      const { brand, model, barcode } = response.data
      remoteLog("File scan result", "INFO", { barcode, brand, model });
      
      if (barcode && !brand && !model) {
          setError(`Barcode detected: ${barcode}, but no product information was found. You may need to enter details manually.`)
      } else {
          setScanning(false)
          onProductFound(brand || '', model || '')
      }
    } catch (err: any) {
      remoteLog("File scan error", "ERROR", { error: err });
      let detail = "Could not detect barcode in image."
      
      if (err.code === 'ECONNABORTED') {
          detail = "Upload timed out. The image might be too large or the server is busy."
      } else if (err.response?.data?.detail) {
          detail = err.response.data.detail
      } else if (err.message) {
          detail = err.message
      }
      
      setError(`Error: ${detail}`)
      
      // Resume scanning
      try {
        if (scannerRef.current && scanning) {
            scannerRef.current.resume()
        }
      } catch (resumeErr) {
          console.warn("Failed to resume scanner:", resumeErr)
      }
    } finally {
      setUploading(false)
      // Reset input
      e.target.value = ''
    }
  }

  return (
    <div className="mb-4">
      {error && <Alert variant="warning">{error}</Alert>}
      
      <div className="mb-3">
        <Form.Group controlId="barcodeImage" className="mb-2">
          <Form.Label>Upload a photo of a barcode</Form.Label>
          <Form.Control 
            type="file" 
            accept="image/*" 
            onChange={handleFileUpload} 
            disabled={uploading}
          />
          {uploading && <Form.Text className="text-muted"><Spinner animation="border" size="sm" /> Scanning image...</Form.Text>}
        </Form.Group>
      </div>

      {!scanning && (error || !uploading) && (
          <Button onClick={handleRestart} variant="secondary" className="mb-3">Start Camera Scan</Button>
      )}

      <div id="reader" style={{ width: '100%', display: scanning ? 'block' : 'none' }}></div>
      
      <div className="text-muted mt-2 small">
        Point your camera at a product barcode (UPC/EAN) or upload a clear photo.
      </div>
    </div>
  )
}

export default ManualBarcode
