'use client'

import { ReactNode } from 'react'
import { Card, CardContent } from '@/components/ui/card'

interface Column<T> {
  key: keyof T | string
  header: string
  render?: (item: T) => ReactNode
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  emptyMessage?: string
}

export function DataTable<T extends Record<string, unknown>>({
  data,
  columns,
  emptyMessage = 'No hay datos disponibles',
}: DataTableProps<T>) {
  if (data.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-gray-600">{emptyMessage}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b bg-gray-50">
            {columns.map((col, idx) => (
              <th
                key={idx}
                className="px-4 py-3 text-left text-sm font-semibold text-gray-700"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, rowIdx) => (
            <tr
              key={rowIdx}
              className="border-b hover:bg-gray-50 transition-colors"
            >
              {columns.map((col, colIdx) => (
                <td key={colIdx} className="px-4 py-3 text-sm">
                  {col.render
                    ? col.render(item)
                    : String(item[col.key as keyof T] || '-')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


