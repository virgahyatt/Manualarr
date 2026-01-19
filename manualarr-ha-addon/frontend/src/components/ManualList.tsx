import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Table, Alert, Spinner, Button, Modal, Form, InputGroup, Container, Row, Col, Badge } from 'react-bootstrap'
import { FaEdit, FaTrash, FaFilePdf, FaSearch, FaExternalLinkAlt } from 'react-icons/fa'

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
  const [searchTerm, setSearchTerm] = useState('')

  // Edit State
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingManual, setEditingManual] = useState<Manual | null>(null)
  const [editForm, setEditForm] = useState({ brand: '', model: '', filename: '' })

  useEffect(() => {
    const fetchManuals = async () => {
      try {
        const response = await axios.get<Manual[]>('api/manuals/')
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
      await axios.delete(`api/manuals/${id}`)
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
      const response = await axios.patch<Manual>(`api/manuals/${editingManual.id}`, editForm)
      setManuals(manuals.map(m => m.id === editingManual.id ? response.data : m))
      setShowEditModal(false)
    } catch (err) {
      alert('Failed to update manual')
      console.error(err)
    }
  }

  const filteredManuals = manuals.filter(manual => {
    const searchLower = searchTerm.toLowerCase()
    return (
      (manual.brand?.toLowerCase() || '').includes(searchLower) ||
      (manual.model?.toLowerCase() || '').includes(searchLower) ||
      (manual.filename?.toLowerCase() || '').includes(searchLower)
    )
  })

  if (loading) return (
    <div className="text-center p-5">
      <Spinner animation="border" role="status">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
  )
  
  if (error) return <Alert variant="danger">{error}</Alert>

  return (
    <Container fluid className="p-0">
      <Row className="mb-3 align-items-center">
        <Col>
          <h4 className="mb-0">My Manuals <Badge bg="secondary" pill>{manuals.length}</Badge></h4>
        </Col>
        <Col xs="auto">
          <InputGroup>
            <InputGroup.Text><FaSearch /></InputGroup.Text>
            <Form.Control
              placeholder="Filter manuals..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
      </Row>

      {manuals.length === 0 ? (
         <Alert variant="info">No manuals found. Upload one to get started!</Alert>
      ) : (
        <div className="table-responsive shadow-sm rounded">
          <Table hover striped bordered className="mb-0 align-middle bg-white">
            <thead className="table-light">
              <tr>
                <th style={{ width: '20%' }}>Brand</th>
                <th style={{ width: '25%' }}>Model</th>
                <th>Filename</th>
                <th style={{ width: '150px' }} className="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredManuals.length > 0 ? (
                filteredManuals.map((manual) => (
                  <tr key={manual.id}>
                    <td className="fw-bold text-primary">{manual.brand}</td>
                    <td>{manual.model}</td>
                    <td className="text-muted small">
                      <FaFilePdf className="me-2 text-danger" />
                      {manual.filename}
                    </td>
                    <td className="text-center">
                      <div className="d-flex justify-content-center gap-2">
                        <Button 
                          variant="outline-primary" 
                          size="sm"
                          href={`api/files/${encodeURIComponent(manual.filename)}`}
                          target="_blank"
                          title="Open PDF"
                        >
                          <FaExternalLinkAlt />
                        </Button>
                        <Button 
                          variant="outline-secondary" 
                          size="sm" 
                          onClick={() => handleEditClick(manual)}
                          title="Edit"
                        >
                          <FaEdit />
                        </Button>
                        <Button 
                          variant="outline-danger" 
                          size="sm" 
                          onClick={() => handleDelete(manual.id)}
                          title="Delete"
                        >
                          <FaTrash />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="text-center text-muted py-4">
                    No matching manuals found.
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </div>
      )}

      <Modal show={showEditModal} onHide={() => setShowEditModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Edit Manual Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Brand</Form.Label>
              <Form.Control 
                type="text" 
                value={editForm.brand} 
                onChange={(e) => setEditForm({...editForm, brand: e.target.value})} 
                placeholder="e.g. Sony"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Model</Form.Label>
              <Form.Control 
                type="text" 
                value={editForm.model} 
                onChange={(e) => setEditForm({...editForm, model: e.target.value})} 
                placeholder="e.g. WH-1000XM4"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Filename</Form.Label>
              <InputGroup>
                <Form.Control 
                  type="text" 
                  value={editForm.filename} 
                  onChange={(e) => setEditForm({...editForm, filename: e.target.value})} 
                />
              </InputGroup>
              <Form.Text className="text-muted">
                 Note: Renaming the file changes its URL.
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
    </Container>
  )
}

export default ManualList