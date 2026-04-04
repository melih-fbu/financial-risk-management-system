import { formatCurrency, formatDate, metalLabels } from '../utils/formatters'

function StatusCard({ metalType, item }) {
  const accentClass = metalType === 'XAU' ? 'from-amber-300 to-yellow-500' : 'from-slate-300 to-slate-500'

  return (
    <article className="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-soft">
      <div className={`mb-6 h-2 w-24 rounded-full bg-gradient-to-r ${accentClass}`} />
      <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
        {metalLabels[metalType]}
      </p>
      <h3 className="mt-4 text-4xl font-bold text-slate-950">{formatCurrency(item?.price_try)}</h3>
      <p className="mt-2 text-sm text-slate-500">Son kayıt tarihi: {formatDate(item?.date)}</p>
      <div className="mt-6 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
        USD fiyatı: <span className="font-semibold text-slate-800">${item?.price_usd?.toFixed?.(2) ?? '-'}</span>
      </div>
    </article>
  )
}

export default StatusCard
