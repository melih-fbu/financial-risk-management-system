import { useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import SectionHeader from '../components/SectionHeader'
import { reportsApi } from '../services/api'
import { formatCurrency, metalLabels } from '../utils/formatters'

const initialForm = {
  initial_amount: '',
  start_date: '',
  end_date: '',
}

function ComparePage() {
  const [formData, setFormData] = useState(initialForm)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target
    setFormData((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    try {
      setLoading(true)
      setError('')
      const response = await reportsApi.compareMetals({
        initial_amount: Number(formData.initial_amount),
        start_date: formData.start_date,
        end_date: formData.end_date,
      })
      setResult(response.data)
    } catch (requestError) {
      setResult(null)
      setError(requestError.response?.data?.detail ?? 'Metal karşılaştırması oluşturulamadı.')
    } finally {
      setLoading(false)
    }
  }

  const chartData = useMemo(() => {
    if (!result?.results) {
      return []
    }

    return Object.values(result.results).map((item) => ({
      metal: metalLabels[item.metal_type],
      finalAmount: item.final_amount,
      profitLoss: item.profit_loss,
      var95: item.var_95,
    }))
  }, [result])

  return (
    <div className="space-y-8">
      <SectionHeader
        eyebrow="Karşılaştırma"
        title="Aynı yatırımı altın ve gümüşte yan yana incele"
        description="Başlangıç ve bitiş tarihi belirleyerek aynı tutarın iki farklı metalde nasıl performans gösterdiğini, kar/zarar ve VaR bazında karşılaştır."
      />

      <section className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <form
          onSubmit={handleSubmit}
          className="space-y-5 rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft"
        >
          <div>
            <label htmlFor="initial_amount" className="mb-2 block text-sm font-semibold text-slate-700">
              Yatırım Tutarı (TL)
            </label>
            <input
              id="initial_amount"
              name="initial_amount"
              type="number"
              min="0"
              step="0.01"
              value={formData.initial_amount}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
              placeholder="10000"
              required
            />
          </div>

          <div>
            <label htmlFor="start_date" className="mb-2 block text-sm font-semibold text-slate-700">
              Başlangıç Tarihi
            </label>
            <input
              id="start_date"
              name="start_date"
              type="date"
              value={formData.start_date}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
              required
            />
          </div>

          <div>
            <label htmlFor="end_date" className="mb-2 block text-sm font-semibold text-slate-700">
              Bitiş Tarihi
            </label>
            <input
              id="end_date"
              name="end_date"
              type="date"
              value={formData.end_date}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-2xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading ? 'Karşılaştırma hesaplanıyor...' : 'Karşılaştır'}
          </button>

          {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div>}
        </form>

        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {['XAU', 'XAG'].map((metalType) => {
              const item = result?.results?.[metalType]
              return (
                <article key={metalType} className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft">
                  <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
                    {metalLabels[metalType]}
                  </p>
                  <p className="mt-4 text-3xl font-bold text-slate-950">
                    {item ? formatCurrency(item.final_amount) : '-'}
                  </p>
                  <div className="mt-5 space-y-2 text-sm text-slate-700">
                    <p>Kar / zarar: {item ? formatCurrency(item.profit_loss) : '-'}</p>
                    <p>VaR %95: {item ? formatCurrency(item.var_95) : '-'}</p>
                    <p>Başlangıç fiyatı: {item ? formatCurrency(item.start_price_try) : '-'}</p>
                    <p>Bitiş fiyatı: {item ? formatCurrency(item.end_price_try) : '-'}</p>
                  </div>
                </article>
              )
            })}
          </div>

          <section className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft">
            <div className="mb-4">
              <h3 className="text-2xl font-bold text-slate-950">Bar Chart Karşılaştırması</h3>
              <p className="mt-2 text-sm text-slate-600">
                Nihai tutar, kar/zarar ve VaR değerleri iki metal arasında aynı eksende gösterilir.
              </p>
            </div>

            <div className="h-[360px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 12, right: 8, left: 0, bottom: 8 }}>
                  <CartesianGrid stroke="#dbe4f0" strokeDasharray="4 4" />
                  <XAxis dataKey="metal" tick={{ fill: '#475569', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#475569', fontSize: 12 }} />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Legend />
                  <Bar dataKey="finalAmount" name="Final Tutar" fill="#0f172a" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="profitLoss" name="Kar / Zarar" fill="#d4a017" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="var95" name="VaR %95" fill="#64748b" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {result?.better_metal && (
              <p className="mt-4 text-sm font-semibold text-slate-700">
                Bu tarih aralığında daha yüksek final tutar üreten metal: {metalLabels[result.better_metal]}
              </p>
            )}
          </section>
        </div>
      </section>
    </div>
  )
}

export default ComparePage
