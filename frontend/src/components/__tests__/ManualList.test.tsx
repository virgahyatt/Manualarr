import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import type { Mocked } from 'vitest'
import ManualList from '../ManualList'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as Mocked<typeof axios>

describe('ManualList', () => {
  it('renders a list of manuals', async () => {
    const manuals = [
      { id: 1, brand: 'Sony', model: 'TV', filename: 'manual.pdf' },
      { id: 2, brand: 'Dell', model: 'Monitor', filename: 'monitor.pdf' },
    ]
    mockedAxios.get.mockResolvedValue({ data: manuals })

    render(<ManualList />)

    await waitFor(() => {
      const link1 = screen.getByText('Sony - TV').closest('a')
      expect(link1).toHaveAttribute('href', '/api/files/manual.pdf')
      
      const link2 = screen.getByText('Dell - Monitor').closest('a')
      expect(link2).toHaveAttribute('href', '/api/files/monitor.pdf')
    })
  })

  it('shows a message when no manuals are found', async () => {
    mockedAxios.get.mockResolvedValue({ data: [] })

    render(<ManualList />)

    await waitFor(() => {
      expect(screen.getByText(/No manuals found/i)).toBeInTheDocument()
    })
  })
})
