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

  useEffect(() => {
    // Initialize scanner
    // Use a unique ID for the element
    const scannerId = "reader"
    
    // Cleanup previous instance if any (React strict mode double invoke)
    if (scannerRef.current) {
        scannerRef.current.clear().catch(console.error)
    }

    const scanner = new Html5QrcodeScanner(
      scannerId,
      {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        experimentalFeatures: {
          useBarCodeDetectorIfSupported: true
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
      /* verbose= */ false
    )
    scannerRef.current = scanner

    scanner.render(onScanSuccess, onScanFailure)

    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear().catch(console.error)
      }
    }
  }, [])

  const onScanSuccess = async (decodedText: string) => {
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
      
      // Pass to parent
      onProductFound(brand || '', model || '')
      
    } catch (err) {
      setError(`Product lookup failed for barcode: ${decodedText}. You may need to search manually.`)
    }
  }

  const onScanFailure = (_error: any) => {
    // handle scan failure, usually better to ignore and keep scanning.
  }
  
  const handleRestart = () => {
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
    console.log("Starting file upload:", file.name)

    const formData = new FormData()
    formData.append('file', file)

    try {
        // Safely pause scanner
        try {
            if (scannerRef.current && scanning) {
                console.log("Pausing camera scanner...")
                scannerRef.current.pause()
            }
        } catch (pauseErr) {
            console.warn("Failed to pause scanner (non-fatal):", pauseErr)
        }

      console.log("Sending request to backend...")
      const response = await axios.post('/api/products/scan-barcode', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 30000 // 30 seconds timeout
      })
      console.log("Response received:", response.data)
      const { brand, model, barcode } = response.data
      
      if (barcode && !brand && !model) {
          setError(`Barcode detected: ${barcode}, but no product information was found. You may need to enter details manually.`)
          // We don't setScanning(false) here so they can try again or see the error
      } else {
          setScanning(false)
          onProductFound(brand || '', model || '')
      }
    } catch (err: any) {
      console.error("Scan Error:", err)
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
