import React, { useState } from 'react'
import axios from 'axios'
import { Form, Button, Alert, ListGroup, Spinner } from 'react-bootstrap'

interface SearchResult {
  source: string
  title: string
  identifier: string
  filename: string
  url: string
  size: number
}

interface ManualSearchProps {
  onImportSuccess: () => void
  initialBrand?: string
  initialModel?: string
}

const ManualSearch: React.FC<ManualSearchProps> = ({ onImportSuccess, initialBrand = '', initialModel = '' }) => {
  const [brand, setBrand] = useState(initialBrand)
  const [model, setModel] = useState(initialModel)
  const [results, setResults] = useState<SearchResult[]>([])
  
  // Update state if props change (e.g. from barcode scan)
  React.useEffect(() => {
      if (initialBrand) setBrand(initialBrand)
      if (initialModel) setModel(initialModel)
  }, [initialBrand, initialModel])
  const [searching, setSearching] = useState(false)
  const [importing, setImporting] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setSearching(true)
    setError(null)
    setResults([])

    try {
      const response = await axios.get<SearchResult[]>('api/manuals/search', {
        params: { brand, model }
      })
      setResults(response.data)
      if (response.data.length === 0) {
        setError('No manuals found.')
      }
    } catch (err) {
      setError('Search failed.')
      console.error(err)
    } finally {
      setSearching(false)
    }
  }

  const handleImport = async (result: SearchResult) => {
    setImporting(result.identifier)
    try {
      await axios.post('api/manuals/import', {
        brand,
        model,
        url: result.url,
        filename: result.filename
      })
      onImportSuccess()
      alert('Manual imported successfully!')
    } catch (err) {
      alert('Failed to import manual.')
      console.error(err)
    } finally {
      setImporting(null)
    }
  }

  return (
    <div className="mb-4">
      <Form onSubmit={handleSearch} className="mb-3">
        <Form.Group className="mb-2">
          <Form.Control 
            type="text" 
            placeholder="Brand (e.g. Sony)" 
            value={brand} 
            onChange={(e) => setBrand(e.target.value)} 
            required 
          />
        </Form.Group>
        <Form.Group className="mb-2">
          <Form.Control 
            type="text" 
            placeholder="Model (e.g. WH-1000XM4)" 
            value={model} 
            onChange={(e) => setModel(e.target.value)} 
            required 
          />
        </Form.Group>
        <Button type="submit" disabled={searching} variant="secondary" className="w-100">
          {searching ? <Spinner animation="border" size="sm" /> : 'Search Internet Archive'}
        </Button>
      </Form>

      {error && <Alert variant="warning">{error}</Alert>}

      <ListGroup>
        {results.map((result) => (
          <ListGroup.Item key={result.identifier + result.filename} className="d-flex justify-content-between align-items-center">
            <div style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
              <strong>{result.title}</strong><br/>
              <small className="text-muted">{result.filename} ({Math.round(result.size / 1024)} KB)</small>
            </div>
            <Button 
              size="sm" 
              variant="success" 
              disabled={importing !== null}
              onClick={() => handleImport(result)}
            >
              {importing === result.identifier ? <Spinner animation="border" size="sm" /> : 'Import'}
            </Button>
          </ListGroup.Item>
        ))}
      </ListGroup>
    </div>
  )
}

export default ManualSearch
