import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import type { Mocked } from 'vitest'
import ManualBarcode from '../ManualBarcode'
import axios from 'axios'

// Mock html5-qrcode
vi.mock('html5-qrcode', () => {
  return {
    Html5QrcodeScanner: class {
      render() {}
      clear() { return Promise.resolve(true) }
      pause() {}
      resume() {}
    }
  }
})

vi.mock('axios')
const mockedAxios = axios as Mocked<typeof axios>

describe('ManualBarcode', () => {
  it('renders scanner', () => {
    const onProductFound = vi.fn()
    render(<ManualBarcode onProductFound={onProductFound} />)
    expect(screen.getByText(/Point your camera/i)).toBeInTheDocument()
  })
})
