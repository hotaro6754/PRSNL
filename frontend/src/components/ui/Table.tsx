import React from 'react'

export function TableContainer({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-lg border border-white/[0.08] bg-[#111318] overflow-hidden ${className}`}
      {...props}
    >
      <div className="overflow-x-auto">
        {children}
      </div>
    </div>
  )
}

export function Table({
  className = '',
  children,
  ...props
}: React.TableHTMLAttributes<HTMLTableElement>) {
  return (
    <table className={`w-full text-left text-xs border-collapse ${className}`} {...props}>
      {children}
    </table>
  )
}

export function TableHeader({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <thead className={`bg-[#0d0f14] border-b border-white/[0.08] text-zinc-400 font-mono select-none ${className}`} {...props}>
      {children}
    </thead>
  )
}

export function TableBody({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <tbody className={`divide-y divide-white/[0.04] text-zinc-300 ${className}`} {...props}>
      {children}
    </tbody>
  )
}

export function TableRow({
  className = '',
  children,
  ...props
}: React.HTMLAttributes<HTMLTableRowElement>) {
  return (
    <tr
      className={`hover:bg-white/[0.03] transition-colors group ${className}`}
      {...props}
    >
      {children}
    </tr>
  )
}

export function TableHead({
  className = '',
  children,
  ...props
}: React.ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={`py-2.5 px-3.5 text-[11px] font-semibold uppercase tracking-wider text-zinc-400 font-mono ${className}`}
      {...props}
    >
      {children}
    </th>
  )
}

export function TableCell({
  className = '',
  children,
  ...props
}: React.TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td
      className={`py-2.5 px-3.5 text-xs text-zinc-300 font-mono align-middle ${className}`}
      {...props}
    >
      {children}
    </td>
  )
}
