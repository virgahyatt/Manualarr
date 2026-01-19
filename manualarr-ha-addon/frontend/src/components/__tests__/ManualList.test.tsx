import { render, screen, waitFor, fireEvent } from '@testing-library/react'
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

  it('deletes a manual', async () => {
    const manuals = [
      { id: 1, brand: 'Sony', model: 'TV', filename: 'manual.pdf' },
    ]
    mockedAxios.get.mockResolvedValue({ data: manuals })
    mockedAxios.delete.mockResolvedValue({})
    
    // Mock window.confirm
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)

    render(<ManualList />)

    await waitFor(() => {
      expect(screen.getByText('Sony - TV')).toBeInTheDocument()
    })

    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(confirmSpy).toHaveBeenCalled()
      expect(mockedAxios.delete).toHaveBeenCalledWith('/api/manuals/1')
      // Should be removed from the list
      expect(screen.queryByText('Sony - TV')).not.toBeInTheDocument()
    })
    
    confirmSpy.mockRestore()
  })

  it('shows a message when no manuals are found', async () => {
    mockedAxios.get.mockResolvedValue({ data: [] })

    render(<ManualList />)

    await waitFor(() => {
      expect(screen.getByText(/No manuals found/i)).toBeInTheDocument()
    })
  })
})