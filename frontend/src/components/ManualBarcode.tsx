import React, { useEffect, useRef, useState } from 'react'
import { Html5QrcodeScanner } from 'html5-qrcode'
import axios from 'axios'
import { Button, Alert } from 'react-bootstrap'

interface ManualBarcodeProps {
  onProductFound: (brand: string, model: string) => void
}

const ManualBarcode: React.FC<ManualBarcodeProps> = ({ onProductFound }) => {
  const [error, setError] = useState<string | null>(null)
  const [scanning, setScanning] = useState(true)
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
      { fps: 10, qrbox: { width: 250, height: 250 } },
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
      // Resume scanning if failed? Or let user decide?
      // Let's let user try again or switch tab
    }
  }

  const onScanFailure = (_error: any) => {
    // handle scan failure, usually better to ignore and keep scanning.
    // console.warn(`Code scan error = ${error}`);
  }
  
  const handleRestart = () => {
      setScanning(true)
      setError(null)
      if (scannerRef.current) {
          scannerRef.current.resume()
      }
  }

  return (
    <div className="mb-4">
      {error && <Alert variant="warning">{error}</Alert>}
      
      {!scanning && error && (
          <Button onClick={handleRestart} variant="secondary" className="mb-3">Scan Again</Button>
      )}

      <div id="reader" style={{ width: '100%' }}></div>
      
      <div className="text-muted mt-2 small">
        Point your camera at a product barcode (UPC/EAN).
      </div>
    </div>
  )
}

export default ManualBarcode
