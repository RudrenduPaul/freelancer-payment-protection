'use client'

import { useCallback, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import {
  Gavel,
  FileText,
  Download,
  Clipboard,
  Check,
  RotateCcw,
  Loader2,
} from 'lucide-react'
import { legalDocsApi } from '@/lib/api'
import type { DemandLetterResponse } from '@/lib/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DisclaimerBanner } from '@/components/legal/disclaimer-banner'

const JURISDICTIONS = [
  { value: 'US-NY', label: 'US - New York' },
  { value: 'US-CA', label: 'US - California' },
  { value: 'UK-EW', label: 'UK - England & Wales' },
  { value: 'CA-ON', label: 'CA - Ontario' },
  { value: 'AU-NSW', label: 'AU - New South Wales' },
]

type GenerationState = 'idle' | 'generating' | 'streaming' | 'done'

export default function LegalPage() {
  const [invoiceId, setInvoiceId] = useState('')
  const [jurisdiction, setJurisdiction] = useState('')
  const [evidenceSummary, setEvidenceSummary] = useState('')

  const [genState, setGenState] = useState<GenerationState>('idle')
  const [streamedText, setStreamedText] = useState('')
  const [letterResponse, setLetterResponse] = useState<DemandLetterResponse | null>(null)
  const [copied, setCopied] = useState(false)

  const abortRef = useRef<AbortController | null>(null)

  const handleGenerate = useCallback(async () => {
    if (!invoiceId.trim() || !jurisdiction) {
      toast.error('Please fill in Invoice ID and Jurisdiction.')
      return
    }

    // Abort any previous stream
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setStreamedText('')
    setLetterResponse(null)
    setCopied(false)
    setGenState('generating')

    try {
      // First call legalDocsApi.create to register + get back document metadata
      const response = await legalDocsApi.create({
        invoiceId: invoiceId.trim(),
        jurisdiction,
        evidenceSummary: evidenceSummary.trim() || undefined,
      })
      setLetterResponse(response)

      // Now stream the letter content
      setGenState('streaming')
      const streamUrl = legalDocsApi.streamUrl(invoiceId.trim(), jurisdiction)

      const fetchResponse = await fetch(streamUrl, {
        signal: controller.signal,
      })

      if (!fetchResponse.ok) {
        throw new Error(`Stream request failed: ${fetchResponse.status}`)
      }

      const reader = fetchResponse.body!.getReader()
      const decoder = new TextDecoder()

      let accumulated = ''

      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        // Handle SSE format: lines starting with "data: "
        const lines = chunk.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') break
            accumulated += data
            setStreamedText(accumulated)
          } else if (line.trim() && !line.startsWith(':')) {
            // Plain text stream (non-SSE fallback)
            accumulated += line
            setStreamedText(accumulated)
          }
        }
      }

      setGenState('done')
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') {
        return
      }
      toast.error('Failed to generate demand letter. Please try again.')
      setGenState('idle')
    }
  }, [invoiceId, jurisdiction, evidenceSummary])

  const handleCopy = useCallback(async () => {
    if (!streamedText) return
    try {
      await navigator.clipboard.writeText(streamedText)
      setCopied(true)
      setTimeout(() => setCopied(false), 2500)
    } catch {
      toast.error('Failed to copy to clipboard.')
    }
  }, [streamedText])

  const handleReset = () => {
    abortRef.current?.abort()
    setGenState('idle')
    setStreamedText('')
    setLetterResponse(null)
    setCopied(false)
    setInvoiceId('')
    setJurisdiction('')
    setEvidenceSummary('')
  }

  const isGenerating = genState === 'generating' || genState === 'streaming'
  const hasContent = genState === 'streaming' || genState === 'done'

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Page header */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-200 bg-white flex-shrink-0">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white flex-shrink-0">
          <Gavel className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-900">Demand Letter Generator</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            AI-powered legal demand letters — jurisdiction-aware, evidence-backed.
          </p>
        </div>
      </div>

      {/* Two-panel layout */}
      <div className="flex flex-1 min-h-0 divide-x divide-slate-200">
        {/* Left panel: form */}
        <div className="w-full max-w-sm flex-shrink-0 overflow-y-auto p-6 space-y-5">
          {/* Invoice ID */}
          <div className="space-y-1.5">
            <Label htmlFor="invoice-id">Invoice ID</Label>
            <Input
              id="invoice-id"
              placeholder="e.g. inv_abc123"
              value={invoiceId}
              onChange={(e) => setInvoiceId(e.target.value)}
              disabled={isGenerating}
              required
            />
          </div>

          {/* Jurisdiction */}
          <div className="space-y-1.5">
            <Label htmlFor="jurisdiction">Jurisdiction</Label>
            <Select
              value={jurisdiction}
              onValueChange={setJurisdiction}
              disabled={isGenerating}
            >
              <SelectTrigger id="jurisdiction">
                <SelectValue placeholder="Select jurisdiction…" />
              </SelectTrigger>
              <SelectContent>
                {JURISDICTIONS.map((j) => (
                  <SelectItem key={j.value} value={j.value}>
                    {j.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Evidence summary */}
          <div className="space-y-1.5">
            <Label htmlFor="evidence">Evidence Summary (optional)</Label>
            <textarea
              id="evidence"
              rows={5}
              placeholder="Describe key evidence: emails, screenshots, contracts…"
              value={evidenceSummary}
              onChange={(e) => setEvidenceSummary(e.target.value)}
              disabled={isGenerating}
              className="w-full resize-none rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          <Button
            className="w-full gap-2"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                {genState === 'generating' ? 'Generating…' : 'Streaming…'}
              </>
            ) : (
              <>
                <FileText className="h-4 w-4" />
                Generate Demand Letter
              </>
            )}
          </Button>
        </div>

        {/* Right panel: preview */}
        <div className="flex-1 overflow-y-auto p-6">
          {!hasContent && genState === 'idle' && (
            <div className="flex h-full min-h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-200">
              <div className="text-center text-slate-400">
                <FileText className="mx-auto mb-3 h-10 w-10 opacity-40" />
                <p className="text-sm font-medium">
                  Your demand letter will appear here with typewriter effect…
                </p>
                <p className="mt-1 text-xs opacity-70">
                  Fill in the form and click Generate
                </p>
              </div>
            </div>
          )}

          {hasContent && (
            <AnimatePresence>
              <motion.div
                key="letter-panel"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                {/* Disclaimer — always shown, non-dismissible */}
                <DisclaimerBanner />

                {/* Letter content */}
                <div className="rounded-xl border border-slate-200 bg-white shadow-md mx-auto"
                  style={{ maxWidth: '65ch' }}>
                  <div className="p-8">
                    <pre
                      className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-slate-800"
                      style={{ fontFamily: "'Courier New', Courier, monospace" }}
                    >
                      {streamedText}
                      {genState === 'streaming' && (
                        <motion.span
                          animate={{ opacity: [1, 0] }}
                          transition={{ repeat: Infinity, duration: 0.8 }}
                          className="inline-block w-0.5 h-4 bg-slate-800 ml-0.5 align-text-bottom"
                        />
                      )}
                    </pre>
                  </div>
                </div>

                {/* Action buttons — only shown when done */}
                {genState === 'done' && letterResponse && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.25 }}
                    className="flex flex-wrap items-center gap-3 mx-auto"
                    style={{ maxWidth: '65ch' }}
                  >
                    {/* Download PDF */}
                    <motion.a
                      href={letterResponse.documentUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-700"
                    >
                      <Download className="h-4 w-4" />
                      Download PDF
                    </motion.a>

                    {/* Copy to clipboard */}
                    <Button
                      variant="outline"
                      className="gap-2"
                      onClick={handleCopy}
                    >
                      <AnimatePresence mode="wait" initial={false}>
                        {copied ? (
                          <motion.span
                            key="check"
                            initial={{ scale: 0.6, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.6, opacity: 0 }}
                            transition={{ type: 'spring', stiffness: 400, damping: 20 }}
                            className="flex items-center gap-1.5 text-emerald-600"
                          >
                            <Check className="h-4 w-4" />
                            Copied!
                          </motion.span>
                        ) : (
                          <motion.span
                            key="clip"
                            initial={{ scale: 0.6, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.6, opacity: 0 }}
                            className="flex items-center gap-1.5"
                          >
                            <Clipboard className="h-4 w-4" />
                            Copy to Clipboard
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </Button>

                    {/* Start over */}
                    <Button
                      variant="ghost"
                      className="gap-2 text-slate-500"
                      onClick={handleReset}
                    >
                      <RotateCcw className="h-4 w-4" />
                      Start Over
                    </Button>
                  </motion.div>
                )}
              </motion.div>
            </AnimatePresence>
          )}
        </div>
      </div>
    </div>
  )
}
