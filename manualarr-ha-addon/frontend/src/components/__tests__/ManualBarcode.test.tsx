import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ManualBarcode from '../ManualBarcode'

// Mock html5-qrcode
vi.mock('html5-qrcode', () => {
  return {
    Html5QrcodeScanner: class {
      render() {}
      clear() { return Promise.resolve(true) }
      pause() {}
      resume() {}
    },
    Html5QrcodeSupportedFormats: {
      EAN_13: 0,
      EAN_8: 1,
      UPC_A: 2,
      UPC_E: 3,
      CODE_128: 4,
      CODE_39: 5,
      QR_CODE: 6
    },
    Html5QrcodeScanType: {
      SCAN_TYPE_CAMERA: 0,
      SCAN_TYPE_FILE: 1
    }
  }
})

vi.mock('axios')

describe('ManualBarcode', () => {
  it('renders scanner', () => {
    const onProductFound = vi.fn()
    render(<ManualBarcode onProductFound={onProductFound} />)
    expect(screen.getByText(/Point your camera/i)).toBeInTheDocument()
  })
})