import React, { useState } from 'react'
import axios from 'axios'
import { Form, Button, Alert, Spinner } from 'react-bootstrap'

interface ManualUploadProps {
  onUploadSuccess: () => void
}

const ManualUpload: React.FC<ManualUploadProps> = ({ onUploadSuccess }) => {
  const [brand, setBrand] = useState('')
  const [model, setModel] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysisMessage, setAnalysisMessage] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] || null
    setFile(selectedFile)
    
    if (selectedFile) {
      extractMetadata(selectedFile)
    }
  }

  const extractMetadata = async (selectedFile: File) => {
    setAnalyzing(true)
    setAnalysisMessage(null)
    
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await axios.post('api/manuals/extract-metadata', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      const { brand: extractedBrand, model: extractedModel } = response.data
      
      let msg = "Analysis complete."
      
      if (extractedBrand) {
        setBrand(extractedBrand)
        msg += ` Found Brand: ${extractedBrand}.`
      }
      if (extractedModel) {
        setModel(extractedModel)
        msg += ` Found Model: ${extractedModel}.`
      }
      
      if (!extractedBrand && !extractedModel) {
        msg += " No metadata found."
      } else {
        msg += " Please verify."
      }
      
      setAnalysisMessage(msg)

    } catch (err) {
      console.error("Metadata extraction failed", err)
      // Don't block the user, just fail silently on auto-fill
    } finally {
      setAnalyzing(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError(null)

    const formData = new FormData()
    if (brand) formData.append('brand', brand)
    if (model) formData.append('model', model)
    formData.append('file', file)

    try {
      await axios.post('api/manuals/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setBrand('')
      setModel('')
      setFile(null)
      setAnalysisMessage(null)
      
      // Reset file input
      const fileInput = document.getElementById('formFile') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      
      onUploadSuccess()
    } catch (err) {
      setError('Failed to upload manual')
      console.error(err)
    } finally {
      setUploading(false)
    }
  }

  return (
    <Form onSubmit={handleSubmit} className="mb-4">
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Form.Group className="mb-3" controlId="formFile">
        <Form.Label>Select Manual (PDF)</Form.Label>
        <Form.Control 
          type="file" 
          accept="application/pdf"
          onChange={handleFileChange}
          required
        />
        {analyzing && <Form.Text className="text-muted"><Spinner animation="border" size="sm" /> Analyzing PDF...</Form.Text>}
        {analysisMessage && <Form.Text className="text-info d-block">{analysisMessage}</Form.Text>}
      </Form.Group>

      <Form.Group className="mb-3" controlId="formBrand">
        <Form.Label>Brand</Form.Label>
        <Form.Control 
          type="text" 
          value={brand} 
          onChange={(e) => setBrand(e.target.value)} 
          placeholder="e.g. Sony"
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formModel">
        <Form.Label>Model</Form.Label>
        <Form.Control 
          type="text" 
          value={model} 
          onChange={(e) => setModel(e.target.value)} 
          placeholder="e.g. WH-1000XM4"
        />
      </Form.Group>

      <Button variant="primary" type="submit" disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </Button>
    </Form>
  )
}

export default ManualUpload