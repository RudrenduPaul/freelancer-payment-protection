'use client'

import { useState } from 'react'
import { toast } from 'sonner'
import { Loader2 } from 'lucide-react'
import { clientsApi } from '@/lib/api'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface AddClientDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

interface FormState {
  name: string
  email: string
  company: string
  industry: string
  country: string
  paymentTermsDays: string
  notes: string
}

const INITIAL_FORM: FormState = {
  name: '',
  email: '',
  company: '',
  industry: '',
  country: '',
  paymentTermsDays: '30',
  notes: '',
}

interface FieldErrors {
  name?: string
  email?: string
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function AddClientDialog({ open, onOpenChange, onSuccess }: AddClientDialogProps) {
  const [form, setForm] = useState<FormState>(INITIAL_FORM)
  const [errors, setErrors] = useState<FieldErrors>({})
  const [loading, setLoading] = useState(false)

  function handleChange(field: keyof FormState, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (errors[field as keyof FieldErrors]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  function validate(): boolean {
    const next: FieldErrors = {}
    if (!form.name.trim()) next.name = 'Name is required'
    if (!form.email.trim()) {
      next.email = 'Email is required'
    } else if (!validateEmail(form.email.trim())) {
      next.email = 'Enter a valid email address'
    }
    setErrors(next)
    return Object.keys(next).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    try {
      await clientsApi.create({
        name: form.name.trim(),
        email: form.email.trim(),
        company: form.company.trim() || undefined,
        industry: form.industry.trim() || undefined,
        country: form.country.trim().slice(0, 2).toUpperCase() || undefined,
        paymentTermsDays: form.paymentTermsDays ? parseInt(form.paymentTermsDays, 10) : 30,
        notes: form.notes.trim() || undefined,
      })
      toast.success('Client added', {
        description: `${form.name.trim()} is now in your Bad Cop CRM.`,
      })
      setForm(INITIAL_FORM)
      setErrors({})
      onSuccess()
      onOpenChange(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to add client'
      toast.error('Could not add client', { description: message })
    } finally {
      setLoading(false)
    }
  }

  function handleOpenChange(next: boolean) {
    if (!loading) {
      if (!next) {
        setForm(INITIAL_FORM)
        setErrors({})
      }
      onOpenChange(next)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New Client</DialogTitle>
        </DialogHeader>
        <DialogDescription>
          Add a client to start tracking invoices and letting your Bad Cop handle late payments.
        </DialogDescription>

        <form onSubmit={handleSubmit} noValidate>
          <div className="space-y-4 px-6 pb-2">
            {/* Name */}
            <div className="space-y-1.5">
              <Label htmlFor="client-name">
                Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="client-name"
                placeholder="Jane Smith"
                value={form.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className={errors.name ? 'border-red-400 focus:ring-red-400' : ''}
                disabled={loading}
                autoFocus
              />
              {errors.name && (
                <p className="text-xs text-red-500">{errors.name}</p>
              )}
            </div>

            {/* Email */}
            <div className="space-y-1.5">
              <Label htmlFor="client-email">
                Email <span className="text-red-500">*</span>
              </Label>
              <Input
                id="client-email"
                type="email"
                placeholder="jane@acmecorp.com"
                value={form.email}
                onChange={(e) => handleChange('email', e.target.value)}
                className={errors.email ? 'border-red-400 focus:ring-red-400' : ''}
                disabled={loading}
              />
              {errors.email && (
                <p className="text-xs text-red-500">{errors.email}</p>
              )}
            </div>

            {/* Company */}
            <div className="space-y-1.5">
              <Label htmlFor="client-company">Company</Label>
              <Input
                id="client-company"
                placeholder="Acme Corp"
                value={form.company}
                onChange={(e) => handleChange('company', e.target.value)}
                disabled={loading}
              />
            </div>

            {/* Industry + Country row */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="client-industry">Industry</Label>
                <Input
                  id="client-industry"
                  placeholder="SaaS, Design, etc."
                  value={form.industry}
                  onChange={(e) => handleChange('industry', e.target.value)}
                  disabled={loading}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="client-country">Country Code</Label>
                <Input
                  id="client-country"
                  placeholder="US"
                  maxLength={2}
                  value={form.country}
                  onChange={(e) => handleChange('country', e.target.value.toUpperCase())}
                  disabled={loading}
                />
              </div>
            </div>

            {/* Payment Terms */}
            <div className="space-y-1.5">
              <Label htmlFor="client-terms">Payment Terms (days)</Label>
              <Input
                id="client-terms"
                type="number"
                min={0}
                max={365}
                placeholder="30"
                value={form.paymentTermsDays}
                onChange={(e) => handleChange('paymentTermsDays', e.target.value)}
                disabled={loading}
              />
            </div>

            {/* Notes */}
            <div className="space-y-1.5">
              <Label htmlFor="client-notes">Notes</Label>
              <textarea
                id="client-notes"
                rows={3}
                placeholder="Any context about this client's payment behavior..."
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
                  Adding…
                </>
              ) : (
                'Add Client'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
