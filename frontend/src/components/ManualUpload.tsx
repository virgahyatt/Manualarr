import React, { useState } from 'react'
import axios from 'axios'
import { Form, Button, Alert } from 'react-bootstrap'

interface ManualUploadProps {
  onUploadSuccess: () => void
}

const ManualUpload: React.FC<ManualUploadProps> = ({ onUploadSuccess }) => {
  const [brand, setBrand] = useState('')
  const [model, setModel] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
      await axios.post('/api/manuals/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      setBrand('')
      setModel('')
      setFile(null)
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
      <Form.Group className="mb-3" controlId="formBrand">
        <Form.Label>Brand</Form.Label>
        <Form.Control 
          type="text" 
          value={brand} 
          onChange={(e) => setBrand(e.target.value)} 
          placeholder="e.g. Sony (Optional - Auto-detect)"
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formModel">
        <Form.Label>Model</Form.Label>
        <Form.Control 
          type="text" 
          value={model} 
          onChange={(e) => setModel(e.target.value)} 
          placeholder="e.g. WH-1000XM4 (Optional - Auto-detect)"
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formFile">
        <Form.Label>Select Manual (PDF)</Form.Label>
        <Form.Control 
          type="file" 
          accept="application/pdf"
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null)}
          required
        />
      </Form.Group>

      <Button variant="primary" type="submit" disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </Button>
    </Form>
  )
}

export default ManualUpload
