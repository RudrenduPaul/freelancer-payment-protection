import { AlertTriangle } from 'lucide-react'

export function DisclaimerBanner() {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
      <AlertTriangle className="h-4 w-4 flex-shrink-0 text-amber-600 mt-0.5" />
      <p className="text-xs leading-relaxed text-amber-800">
        <span className="font-semibold">Legal Disclaimer: </span>
        This document was generated with AI assistance and does not constitute legal advice.
        Review with a qualified attorney before sending.
      </p>
    </div>
  )
}
