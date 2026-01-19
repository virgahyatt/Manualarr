import { useState } from 'react'
import { Container, Navbar, Row, Col, Tabs, Tab } from 'react-bootstrap'
import ManualUpload from './components/ManualUpload'
import ManualList from './components/ManualList'
import ManualSearch from './components/ManualSearch'
import ManualImportUrl from './components/ManualImportUrl'
import ManualBarcode from './components/ManualBarcode'
import 'bootstrap/dist/css/bootstrap.min.css'

function App() {
  const [refreshKey, setRefreshKey] = useState(0)
  const [activeTab, setActiveTab] = useState('upload')
  const [searchBrand, setSearchBrand] = useState('')
  const [searchModel, setSearchModel] = useState('')

  const handleSuccess = () => {
    setRefreshKey(prev => prev + 1)
  }

  const handleProductFound = (brand: string, model: string) => {
    setSearchBrand(brand)
    setSearchModel(model)
    setActiveTab('search')
  }

  return (
    <>
      <Navbar bg="dark" variant="dark" className="mb-4">
        <Container>
          <Navbar.Brand href="#home">Manualarr</Navbar.Brand>
        </Container>
      </Navbar>

      <Container>
        <Row>
          <Col md={5}>
            <h3>Add Manual</h3>
            <Tabs 
              activeKey={activeTab} 
              onSelect={(k) => setActiveTab(k || 'upload')} 
              id="add-manual-tabs" 
              className="mb-3"
            >
              <Tab eventKey="upload" title="Upload">
                <ManualUpload onUploadSuccess={handleSuccess} />
              </Tab>
              <Tab eventKey="search" title="Search Online">
                <ManualSearch 
                  onImportSuccess={handleSuccess} 
                  initialBrand={searchBrand}
                  initialModel={searchModel}
                />
              </Tab>
              <Tab eventKey="barcode" title="Scan Barcode">
                <ManualBarcode onProductFound={handleProductFound} />
              </Tab>
              <Tab eventKey="import" title="Direct Link">
                <ManualImportUrl onImportSuccess={handleSuccess} />
              </Tab>
            </Tabs>
          </Col>
          <Col md={7}>
            <h3>Stored Manuals</h3>
            <ManualList key={refreshKey} />
          </Col>
        </Row>
      </Container>
    </>
  )
}

export default App
