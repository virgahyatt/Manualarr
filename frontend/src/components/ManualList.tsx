import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { ListGroup, Alert, Spinner } from 'react-bootstrap'

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

  if (loading) return <Spinner animation="border" />
  if (error) return <Alert variant="danger">{error}</Alert>

  if (manuals.length === 0) {
    return <Alert variant="info">No manuals found</Alert>
  }

  return (
    <ListGroup>
      {manuals.map((manual) => (
        <ListGroup.Item key={manual.id}>
          <strong>{manual.brand} - {manual.model}</strong> ({manual.filename})
        </ListGroup.Item>
      ))}
    </ListGroup>
  )
}

export default ManualList
