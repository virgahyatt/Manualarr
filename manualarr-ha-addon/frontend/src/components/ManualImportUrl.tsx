import React, { useState } from 'react'
import axios from 'axios'
import { Form, Button, Alert, Spinner } from 'react-bootstrap'

interface ManualImportUrlProps {
  onImportSuccess: () => void
}

const ManualImportUrl: React.FC<ManualImportUrlProps> = ({ onImportSuccess }) => {
  const [url, setUrl] = useState('')
  const [brand, setBrand] = useState('')
  const [model, setModel] = useState('')
  const [importing, setImporting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setImporting(true)
    setError(null)
    setSuccessMsg(null)

    try {
      await axios.post('api/manuals/import', {
        url,
        brand: brand || null, // Send null if empty to trigger auto-detect
        model: model || null
      })
      setSuccessMsg('Manual imported successfully!')
      setUrl('')
      setBrand('')
      setModel('')
      onImportSuccess()
    } catch (err) {
      setError('Failed to import manual. Please check the URL.')
      console.error(err)
    } finally {
      setImporting(false)
    }
  }

  return (
    <Form onSubmit={handleSubmit} className="mb-4">
      {error && <Alert variant="danger">{error}</Alert>}
      {successMsg && <Alert variant="success">{successMsg}</Alert>}

      <Form.Group className="mb-3" controlId="formUrl">
        <Form.Label>Direct PDF Link (URL)</Form.Label>
        <Form.Control 
          type="url" 
          placeholder="https://example.com/manual.pdf" 
          value={url} 
          onChange={(e) => setUrl(e.target.value)} 
          required 
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formBrand">
        <Form.Label>Brand</Form.Label>
        <Form.Control 
          type="text" 
          placeholder="Optional (Auto-detect)" 
          value={brand} 
          onChange={(e) => setBrand(e.target.value)} 
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formModel">
        <Form.Label>Model</Form.Label>
        <Form.Control 
          type="text" 
          placeholder="Optional (Auto-detect)" 
          value={model} 
          onChange={(e) => setModel(e.target.value)} 
        />
      </Form.Group>

      <Button variant="primary" type="submit" disabled={importing}>
        {importing ? <Spinner animation="border" size="sm" /> : 'Import'}
      </Button>
    </Form>
  )
}

export default ManualImportUrl
