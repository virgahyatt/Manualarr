import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { ListGroup, Alert, Spinner, Button, Modal, Form } from 'react-bootstrap'

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

  // Edit State
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingManual, setEditingManual] = useState<Manual | null>(null)
  const [editForm, setEditForm] = useState({ brand: '', model: '', filename: '' })

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

  const handleEditClick = (manual: Manual) => {
    setEditingManual(manual)
    setEditForm({
      brand: manual.brand || '',
      model: manual.model || '',
      filename: manual.filename || ''
    })
    setShowEditModal(true)
  }

  const handleEditSubmit = async () => {
    if (!editingManual) return

    try {
      const response = await axios.patch<Manual>(`/api/manuals/${editingManual.id}`, editForm)
      setManuals(manuals.map(m => m.id === editingManual.id ? response.data : m))
      setShowEditModal(false)
    } catch (err) {
      alert('Failed to update manual')
      console.error(err)
    }
  }

  if (loading) return <Spinner animation="border" />
  if (error) return <Alert variant="danger">{error}</Alert>

  if (manuals.length === 0) {
    return <Alert variant="info">No manuals found</Alert>
  }

  return (
    <>
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
            <div>
              <Button 
                variant="secondary" 
                size="sm" 
                className="me-2"
                onClick={(e) => {
                  e.stopPropagation()
                  handleEditClick(manual)
                }}
              >
                Edit
              </Button>
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
            </div>
          </ListGroup.Item>
        ))}
      </ListGroup>

      <Modal show={showEditModal} onHide={() => setShowEditModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Manual</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Brand</Form.Label>
              <Form.Control 
                type="text" 
                value={editForm.brand} 
                onChange={(e) => setEditForm({...editForm, brand: e.target.value})} 
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Model</Form.Label>
              <Form.Control 
                type="text" 
                value={editForm.model} 
                onChange={(e) => setEditForm({...editForm, model: e.target.value})} 
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Filename</Form.Label>
              <Form.Control 
                type="text" 
                value={editForm.filename} 
                onChange={(e) => setEditForm({...editForm, filename: e.target.value})} 
              />
              <Form.Text className="text-muted">
                Changing this will rename the file on the server.
              </Form.Text>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowEditModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleEditSubmit}>
            Save Changes
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  )
}

export default ManualList