import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'sonner'
import { SidebarLayout } from '@/components/layout/sidebar-layout'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Bad Cop CRM | Freelancer Payment Protection',
  description:
    'Automate invoice escalation and legal demand letters. Let the Bad Cop handle collections so you keep the relationship.',
  keywords: ['freelancer', 'invoice', 'payment', 'collections', 'legal', 'crm'],
  authors: [
    { name: 'Rudrendu Paul' },
    { name: 'Sourav Nandy' },
  ],
  robots: 'noindex, nofollow',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <SidebarLayout>{children}</SidebarLayout>
        <Toaster
          position="bottom-right"
          toastOptions={{
            classNames: {
              toast:
                'bg-white border border-slate-200 shadow-lg rounded-lg text-slate-900 text-sm',
              title: 'font-semibold',
              description: 'text-slate-500',
              actionButton: 'bg-brand-600 text-white hover:bg-brand-700',
              cancelButton: 'bg-slate-100 text-slate-700 hover:bg-slate-200',
              error: 'border-red-200 bg-red-50 text-red-900',
              success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
            },
          }}
        />
      </body>
    </html>
  )
}
