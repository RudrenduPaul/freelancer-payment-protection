'use client'

import { useEffect, useState, useCallback } from 'react'
import { toast } from 'sonner'
import { Loader2, Plus, Trash2 } from 'lucide-react'
import { clientsApi, invoicesApi } from '@/lib/api'
import type { Client, LineItem } from '@/lib/types'
import { formatCurrency } from '@/lib/utils'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface AddInvoiceDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
  defaultClientId?: string
}

interface FormState {
  clientId: string
  invoiceNumber: string
  amount: string
  currency: string
  issueDate: string
  dueDate: string
  notes: string
}

interface LineItemDraft {
  id: string
  description: string
  quantity: string
  unitPrice: string
}

const CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'SGD', 'INR']

function today(): string {
  return new Date().toISOString().split('T')[0]
}

function thirtyDaysOut(): string {
  const d = new Date()
  d.setDate(d.getDate() + 30)
  return d.toISOString().split('T')[0]
}

function newLineItem(): LineItemDraft {
  return { id: crypto.randomUUID(), description: '', quantity: '1', unitPrice: '' }
}

function lineItemTotal(item: LineItemDraft): number {
  const q = parseFloat(item.quantity) || 0
  const p = parseFloat(item.unitPrice) || 0
  return q * p
}

const INITIAL_FORM: FormState = {
  clientId: '',
  invoiceNumber: '',
  amount: '',
  currency: 'USD',
  issueDate: today(),
  dueDate: thirtyDaysOut(),
  notes: '',
}

interface FieldErrors {
  clientId?: string
  invoiceNumber?: string
  amount?: string
  issueDate?: string
  dueDate?: string
}

export function AddInvoiceDialog({
  open,
  onOpenChange,
  onSuccess,
  defaultClientId,
}: AddInvoiceDialogProps) {
  const [form, setForm] = useState<FormState>({
    ...INITIAL_FORM,
    clientId: defaultClientId ?? '',
  })
  const [lineItems, setLineItems] = useState<LineItemDraft[]>([])
  const [errors, setErrors] = useState<FieldErrors>({})
  const [loading, setLoading] = useState(false)
  const [clients, setClients] = useState<Client[]>([])
  const [clientsLoading, setClientsLoading] = useState(false)

  const loadClients = useCallback(async () => {
    setClientsLoading(true)
    try {
      const res = await clientsApi.list()
      setClients(res.items)
    } catch {
      // silently fail — user can still type client id
    } finally {
      setClientsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (open) {
      loadClients()
      setForm({ ...INITIAL_FORM, clientId: defaultClientId ?? '' })
      setLineItems([])
      setErrors({})
    }
  }, [open, defaultClientId, loadClients])

  // Computed grand total from line items
  const lineItemsTotal = lineItems.reduce((sum, item) => sum + lineItemTotal(item), 0)
  const hasLineItems = lineItems.length > 0

  function handleChange(field: keyof FormState, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (errors[field as keyof FieldErrors]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  function addLineItem() {
    setLineItems((prev) => [...prev, newLineItem()])
  }

  function removeLineItem(id: string) {
    setLineItems((prev) => prev.filter((item) => item.id !== id))
  }

  function updateLineItem(id: string, field: keyof Omit<LineItemDraft, 'id'>, value: string) {
    setLineItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, [field]: value } : item)),
    )
  }

  function validate(): boolean {
    const next: FieldErrors = {}
    if (!form.clientId) next.clientId = 'Select a client'
    if (!form.invoiceNumber.trim()) next.invoiceNumber = 'Invoice number is required'
    if (!hasLineItems) {
      if (!form.amount.trim()) next.amount = 'Enter an amount or add line items'
      else if (isNaN(parseFloat(form.amount)) || parseFloat(form.amount) <= 0)
        next.amount = 'Amount must be a positive number'
    }
    if (!form.issueDate) next.issueDate = 'Issue date is required'
    if (!form.dueDate) next.dueDate = 'Due date is required'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return

    const finalAmount = hasLineItems ? lineItemsTotal : parseFloat(form.amount)
    const finalLineItems: LineItem[] = hasLineItems
      ? lineItems
          .filter((item) => item.description.trim())
          .map((item) => ({
            description: item.description.trim(),
            quantity: parseFloat(item.quantity) || 1,
            unitPrice: parseFloat(item.unitPrice) || 0,
            total: lineItemTotal(item),
          }))
      : []

    setLoading(true)
    try {
      await invoicesApi.create({
        clientId: form.clientId,
        invoiceNumber: form.invoiceNumber.trim(),
        amount: finalAmount,
        currency: form.currency,
        issueDate: form.issueDate,
        dueDate: form.dueDate,
        lineItems: finalLineItems.length > 0 ? finalLineItems : undefined,
        notes: form.notes.trim() || undefined,
      })
      toast.success('Invoice created', {
        description: `${form.invoiceNumber} has been added to Bad Cop CRM.`,
      })
      onSuccess()
      onOpenChange(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create invoice'
      toast.error('Could not create invoice', { description: message })
    } finally {
      setLoading(false)
    }
  }

  function handleOpenChange(next: boolean) {
    if (!loading) onOpenChange(next)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Invoice</DialogTitle>
        </DialogHeader>
        <DialogDescription>
          Track a new invoice and let Bad Cop handle the follow-ups.
        </DialogDescription>

        <form onSubmit={handleSubmit} noValidate>
          <div className="space-y-5 px-6 pb-2">
            {/* Client */}
            <div className="space-y-1.5">
              <Label htmlFor="inv-client">
                Client <span className="text-red-500">*</span>
              </Label>
              <Select
                value={form.clientId}
                onValueChange={(v) => handleChange('clientId', v)}
                disabled={loading || clientsLoading}
              >
                <SelectTrigger
                  id="inv-client"
                  className={errors.clientId ? 'border-red-400' : ''}
                >
                  <SelectValue
                    placeholder={clientsLoading ? 'Loading clients…' : 'Select a client'}
                  />
                </SelectTrigger>
                <SelectContent>
                  {clients.map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.name}
                      {c.company ? ` — ${c.company}` : ''}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.clientId && (
                <p className="text-xs text-red-500">{errors.clientId}</p>
              )}
            </div>

            {/* Invoice Number */}
            <div className="space-y-1.5">
              <Label htmlFor="inv-number">
                Invoice Number <span className="text-red-500">*</span>
              </Label>
              <Input
                id="inv-number"
                placeholder="INV-2025-001"
                value={form.invoiceNumber}
                onChange={(e) => handleChange('invoiceNumber', e.target.value)}
                className={errors.invoiceNumber ? 'border-red-400' : ''}
                disabled={loading}
              />
              {errors.invoiceNumber && (
                <p className="text-xs text-red-500">{errors.invoiceNumber}</p>
              )}
            </div>

            {/* Amount + Currency (shown when no line items) */}
            {!hasLineItems && (
              <div className="grid grid-cols-[1fr_120px] gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="inv-amount">
                    Amount <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="inv-amount"
                    type="number"
                    min={0}
                    step="0.01"
                    placeholder="0.00"
                    value={form.amount}
                    onChange={(e) => handleChange('amount', e.target.value)}
                    className={errors.amount ? 'border-red-400' : ''}
                    disabled={loading}
                  />
                  {errors.amount && (
                    <p className="text-xs text-red-500">{errors.amount}</p>
                  )}
                </div>
                <div className="space-y-1.5">
                  <Label>Currency</Label>
                  <Select
                    value={form.currency}
                    onValueChange={(v) => handleChange('currency', v)}
                    disabled={loading}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CURRENCIES.map((c) => (
                        <SelectItem key={c} value={c}>
                          {c}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            {/* Line Items */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Line Items (optional)</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addLineItem}
                  disabled={loading}
                >
                  <Plus className="h-3.5 w-3.5" />
                  Add Line
                </Button>
              </div>

              {lineItems.length > 0 && (
                <div className="rounded-lg border border-slate-200 overflow-hidden">
                  {/* Line item header */}
                  <div className="grid grid-cols-[1fr_80px_100px_80px_36px] gap-2 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-500">
                    <span>Description</span>
                    <span>Qty</span>
                    <span>Unit Price</span>
                    <span>Total</span>
                    <span />
                  </div>
                  {lineItems.map((item) => (
                    <div
                      key={item.id}
                      className="grid grid-cols-[1fr_80px_100px_80px_36px] gap-2 border-t border-slate-100 px-3 py-2 items-center"
                    >
                      <Input
                        placeholder="Service description"
                        value={item.description}
                        onChange={(e) => updateLineItem(item.id, 'description', e.target.value)}
                        disabled={loading}
                        className="h-8 text-xs"
                      />
                      <Input
                        type="number"
                        min={0}
                        step="0.01"
                        placeholder="1"
                        value={item.quantity}
                        onChange={(e) => updateLineItem(item.id, 'quantity', e.target.value)}
                        disabled={loading}
                        className="h-8 text-xs"
                      />
                      <Input
                        type="number"
                        min={0}
                        step="0.01"
                        placeholder="0.00"
                        value={item.unitPrice}
                        onChange={(e) => updateLineItem(item.id, 'unitPrice', e.target.value)}
                        disabled={loading}
                        className="h-8 text-xs"
                      />
                      <span className="text-xs font-medium text-slate-700 tabular-nums">
                        {formatCurrency(lineItemTotal(item), form.currency)}
                      </span>
                      <button
                        type="button"
                        onClick={() => removeLineItem(item.id)}
                        disabled={loading}
                        className="flex h-7 w-7 items-center justify-center rounded-md text-slate-400 hover:bg-red-50 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                  {/* Total row */}
                  <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-3 py-2">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-semibold text-slate-600">Grand Total</span>
                      <Select
                        value={form.currency}
                        onValueChange={(v) => handleChange('currency', v)}
                        disabled={loading}
                      >
                        <SelectTrigger className="h-7 w-20 text-xs">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {CURRENCIES.map((c) => (
                            <SelectItem key={c} value={c}>
                              {c}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <span className="text-sm font-bold text-slate-900">
                      {formatCurrency(lineItemsTotal, form.currency)}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="inv-issue">
                  Issue Date <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="inv-issue"
                  type="date"
                  value={form.issueDate}
                  onChange={(e) => handleChange('issueDate', e.target.value)}
                  className={errors.issueDate ? 'border-red-400' : ''}
                  disabled={loading}
                />
                {errors.issueDate && (
                  <p className="text-xs text-red-500">{errors.issueDate}</p>
                )}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="inv-due">
                  Due Date <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="inv-due"
                  type="date"
                  value={form.dueDate}
                  onChange={(e) => handleChange('dueDate', e.target.value)}
                  className={errors.dueDate ? 'border-red-400' : ''}
                  disabled={loading}
                />
                {errors.dueDate && (
                  <p className="text-xs text-red-500">{errors.dueDate}</p>
                )}
              </div>
            </div>

            {/* Notes */}
            <div className="space-y-1.5">
              <Label htmlFor="inv-notes">Notes</Label>
              <textarea
                id="inv-notes"
                rows={2}
                placeholder="Payment instructions, project details…"
                value={form.notes}
                onChange={(e) => handleChange('notes', e.target.value)}
                disabled={loading}
                className="flex w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-400 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
              />
            </div>
          </div>

          <DialogFooter className="mt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Creating…
                </>
              ) : (
                'Create Invoice'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
