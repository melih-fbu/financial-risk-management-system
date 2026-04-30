import { useMemo, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import SectionHeader from '../components/SectionHeader'
import { reportsApi } from '../services/api'
import { formatCurrency, metalLabels } from '../utils/formatters'

const initialForm = {
  metal_type: 'XAU',
  days_ahead: 7,
}

function PredictionPage() {
  const [formData, setFormData] = useState(initialForm)
  const [prediction, setPrediction] = useState(null)
  const [signalReport, setSignalReport] = useState(null)
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
      const [predictionResponse, signalResponse] = await Promise.all([
        reportsApi.predictMetal(formData.metal_type, Number(formData.days_ahead)),
        reportsApi.getSignal(formData.metal_type),
      ])
      setPrediction(predictionResponse.data)
      setSignalReport(signalResponse.data)
    } catch (requestError) {
      setPrediction(null)
      setSignalReport(null)
      setError(requestError.response?.data?.detail ?? 'Makine öğrenmesi tahmini alınamadı.')
    } finally {
      setLoading(false)
    }
  }

  const chartData = useMemo(() => {
    if (!prediction) {
      return []
    }

    return [
      { label: 'Bugün', actual: prediction.last_price, predicted: prediction.last_price },
      ...prediction.predicted_prices.map((item) => ({
        label: `+${item.day}. gün`,
        predicted: item.predicted_price,
      })),
    ]
  }, [prediction])

  const riskBarClass =
    signalReport?.risk_level === 'high'
      ? 'bg-rose-500'
      : signalReport?.risk_level === 'medium'
        ? 'bg-amber-500'
        : 'bg-emerald-500'

  const signalCardClass =
    signalReport?.signal?.includes('BUY')
      ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
      : signalReport?.signal?.includes('SELL')
        ? 'border-rose-200 bg-rose-50 text-rose-800'
        : 'border-slate-200 bg-slate-50 text-slate-800'

  return (
    <div className="space-y-8">
      <SectionHeader
        eyebrow="Tahmin"
        title="Makine öğrenmesi ile metal fiyat tahmini üret"
        description="Scikit-learn tabanlı regresyon modeli, geçmiş fiyat serisinden öğrenerek altın veya gümüş için ileri tarihli fiyat tahminleri üretir."
      />

      <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <form
          onSubmit={handleSubmit}
          className="space-y-5 rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft"
        >
          <div>
            <label htmlFor="metal_type" className="mb-2 block text-sm font-semibold text-slate-700">
              Metal Türü
            </label>
            <select
              id="metal_type"
              name="metal_type"
              value={formData.metal_type}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
            >
              <option value="XAU">Altın (XAU)</option>
              <option value="XAG">Gümüş (XAG)</option>
            </select>
          </div>

          <div>
            <label htmlFor="days_ahead" className="mb-2 block text-sm font-semibold text-slate-700">
              Tahmin Ufku
            </label>
            <input
              id="days_ahead"
              name="days_ahead"
              type="number"
              min="1"
              max="60"
              value={formData.days_ahead}
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
            {loading ? 'Tahmin üretiliyor...' : 'Tahmini Çalıştır'}
          </button>

          {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div>}
        </form>

        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-4">
            {[
              {
                label: 'Son Fiyat',
                value: prediction ? formatCurrency(prediction.last_price) : '-',
              },
              {
                label: 'Ortalama Tahmin',
                value: prediction ? formatCurrency(prediction.mean_predicted_price) : '-',
              },
              {
                label: 'Trend',
                value: prediction ? prediction.trend : '-',
              },
              {
                label: 'Veri Sayısı',
                value: prediction ? `${prediction.training_points}` : '-',
              },
            ].map((item) => (
              <article key={item.label} className="rounded-3xl border border-white/70 bg-white/85 p-5 shadow-soft">
                <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">{item.label}</p>
                <p className="mt-4 text-3xl font-bold text-slate-950">{item.value}</p>
              </article>
            ))}
          </div>

          <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
            <article className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">Risk Skoru</p>
              <p className="mt-4 text-4xl font-bold text-slate-950">
                {signalReport ? signalReport.risk_score.toFixed(2) : '-'}
              </p>
              <p className="mt-1 text-sm text-slate-600">
                {signalReport ? signalReport.risk_label : 'Risk skoru bekleniyor'}
              </p>
              <div className="mt-5 h-4 overflow-hidden rounded-full bg-slate-200">
                <div
                  className={`h-full rounded-full ${riskBarClass}`}
                  style={{ width: `${Math.min(signalReport?.risk_score ?? 0, 100)}%` }}
                />
              </div>
              <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
                <p>
                  Volatilite: {signalReport ? `%${signalReport.volatility_pct.toFixed(2)}` : '-'}
                </p>
                <p>
                  Sınıf: {signalReport ? signalReport.volatility_label : '-'}
                </p>
              </div>
            </article>

            <article className={`rounded-[2rem] border p-6 shadow-soft ${signalCardClass}`}>
              <p className="text-sm font-semibold uppercase tracking-[0.25em]">Sinyal</p>
              <p className="mt-4 text-4xl font-bold">
                {signalReport ? signalReport.signal : '-'}
              </p>
              <p className="mt-2 text-sm">
                Güç: {signalReport ? signalReport.signal_strength : '-'}
              </p>
              <div className="mt-5 space-y-2 text-sm">
                <p>
                  Güncel fiyat: {signalReport ? formatCurrency(signalReport.current_price) : '-'}
                </p>
                <p>
                  MA20: {signalReport ? formatCurrency(signalReport.moving_average_20) : '-'}
                </p>
              </div>
              <p className="mt-5 text-sm leading-6">
                {signalReport ? signalReport.reasoning : 'Sinyal açıklaması bekleniyor.'}
              </p>
            </article>
          </section>

          <section className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft">
            <div className="mb-4">
              <h3 className="text-2xl font-bold text-slate-950">
                Fiyat Tahmin Grafiği {prediction ? `- ${metalLabels[prediction.metal_type]}` : ''}
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Grafik son gözlemlenen fiyatı ve sonraki günler için modelin ürettiği tahminleri gösterir.
              </p>
            </div>

            <div className="h-[380px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 12, right: 8, left: 0, bottom: 8 }}>
                  <CartesianGrid stroke="#dbe4f0" strokeDasharray="4 4" />
                  <XAxis dataKey="label" tick={{ fill: '#475569', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#475569', fontSize: 12 }} />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Legend />
                  <Line type="monotone" dataKey="actual" name="Son Gerçek Fiyat" stroke="#0f172a" strokeWidth={3} dot />
                  <Line type="monotone" dataKey="predicted" name="Tahmin" stroke="#d4a017" strokeWidth={3} dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>
      </section>
    </div>
  )
}

export default PredictionPage
