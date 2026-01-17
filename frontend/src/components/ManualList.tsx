import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { ListGroup, Alert, Spinner, Button } from 'react-bootstrap'

interface Manual {
  id: number
  brand: string
  model: string
  filename: string
  filepath: string
}

const ManualList: React.FC = () => {
  const [manuals, setManuals] = useState<Manual[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchManuals = async () => {
      try {
        const response = await axios.get<Manual[]>('/api/manuals/')
        setManuals(response.data)
      } catch (err) {
        setError('Failed to fetch manuals')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchManuals()
  }, [])

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this manual?')) return

    try {
      await axios.delete(`/api/manuals/${id}`)
      setManuals(manuals.filter(m => m.id !== id))
    } catch (err) {
      alert('Failed to delete manual')
      console.error(err)
    }
  }

  if (loading) return <Spinner animation="border" />
  if (error) return <Alert variant="danger">{error}</Alert>

  if (manuals.length === 0) {
    return <Alert variant="info">No manuals found</Alert>
  }

  return (
    <ListGroup>
      {manuals.map((manual) => (
        <ListGroup.Item key={manual.id} className="d-flex justify-content-between align-items-center">
          <a 
            href={`/api/files/${encodeURIComponent(manual.filename)}`} 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ textDecoration: 'none', color: 'inherit', flexGrow: 1 }}
          >
            <strong>{manual.brand} - {manual.model}</strong> ({manual.filename})
          </a>
          <Button 
            variant="danger" 
            size="sm" 
            onClick={(e) => {
              e.stopPropagation()
              handleDelete(manual.id)
            }}
          >
            Delete
          </Button>
        </ListGroup.Item>
      ))}
    </ListGroup>
  )
}

export default ManualList