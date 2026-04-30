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
import { metalLabels } from '../utils/formatters'

const initialForm = {
  metal_type: 'XAU',
  days: 30,
  simulations: 200,
}

function AnalysisPage() {
  const [formData, setFormData] = useState(initialForm)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [monteCarloResult, setMonteCarloResult] = useState(null)
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

      const [analysisResponse, monteCarloResponse] = await Promise.all([
        reportsApi.getMetalAnalysis(formData.metal_type),
        reportsApi.runMonteCarlo({
          metal_type: formData.metal_type,
          days: Number(formData.days),
          simulations: Number(formData.simulations),
        }),
      ])

      setAnalysisResult(analysisResponse.data)
      setMonteCarloResult(monteCarloResponse.data)
    } catch (requestError) {
      setAnalysisResult(null)
      setMonteCarloResult(null)
      setError(requestError.response?.data?.detail ?? 'Metal analizi alınamadı.')
    } finally {
      setLoading(false)
    }
  }

  const chartData = useMemo(() => {
    if (!monteCarloResult?.all_simulations?.length) {
      return []
    }

    const limitedSimulations = monteCarloResult.all_simulations.slice(0, 20)
    const totalDays = limitedSimulations[0]?.length ?? 0

    return Array.from({ length: totalDays }, (_, index) => {
      const row = { day: index }
      limitedSimulations.forEach((simulation, simulationIndex) => {
        row[`sim_${simulationIndex + 1}`] = simulation[index]
      })
      return row
    })
  }, [monteCarloResult])

  return (
    <div className="space-y-8">
      <SectionHeader
        eyebrow="Analiz"
        title="Metal riski ve Monte Carlo tahminlerini tek ekranda incele"
        description="Seçilen metal için Sharpe Ratio, volatilite, max drawdown ve Historical VaR değerlerini görüntüle. Aynı ekranda Monte Carlo fiyat yollarını grafik üzerinden karşılaştır."
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
            <label htmlFor="days" className="mb-2 block text-sm font-semibold text-slate-700">
              Tahmin Gün Sayısı
            </label>
            <input
              id="days"
              name="days"
              type="number"
              min="1"
              value={formData.days}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-slate-400"
              required
            />
          </div>

          <div>
            <label htmlFor="simulations" className="mb-2 block text-sm font-semibold text-slate-700">
              Simülasyon Sayısı
            </label>
            <input
              id="simulations"
              name="simulations"
              type="number"
              min="10"
              step="10"
              value={formData.simulations}
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
            {loading ? 'Analiz hazırlanıyor...' : 'Analizi Çalıştır'}
          </button>

          {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div>}
        </form>

        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {[
              {
                label: 'Sharpe Ratio',
                value: analysisResult ? analysisResult.sharpe_ratio.toFixed(2) : '-',
              },
              {
                label: 'Volatilite',
                value: analysisResult ? `%${analysisResult.volatility.toFixed(2)}` : '-',
              },
              {
                label: 'Max Drawdown',
                value: analysisResult ? `%${analysisResult.max_drawdown.toFixed(2)}` : '-',
              },
              {
                label: 'Historical VaR',
                value: analysisResult ? `%${(analysisResult.historical_var_95 * 100).toFixed(2)}` : '-',
              },
            ].map((item) => (
              <article key={item.label} className="rounded-3xl border border-white/70 bg-white/85 p-5 shadow-soft">
                <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">{item.label}</p>
                <p className="mt-4 text-3xl font-bold text-slate-950">{item.value}</p>
              </article>
            ))}
          </div>

          <section className="rounded-[2rem] border border-white/70 bg-white/85 p-6 shadow-soft">
            <div className="mb-4">
              <h3 className="text-2xl font-bold text-slate-950">
                Monte Carlo Fiyat Yolları {analysisResult ? `- ${metalLabels[analysisResult.metal_type]}` : ''}
              </h3>
              <p className="mt-2 text-sm text-slate-600">
                Aşağıdaki grafik performans için ilk 20 fiyat yolunu gösterir. Kartlarda ortalama, en kötü %5 ve en iyi %95 senaryoları görebilirsin.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Ortalama</p>
                <p className="mt-2 text-2xl font-bold text-slate-950">
                  {monteCarloResult ? monteCarloResult.mean_price.toFixed(2) : '-'}
                </p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm uppercase tracking-[0.25em] text-slate-500">En Kötü %5</p>
                <p className="mt-2 text-2xl font-bold text-slate-950">
                  {monteCarloResult ? monteCarloResult.worst_case.toFixed(2) : '-'}
                </p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="text-sm uppercase tracking-[0.25em] text-slate-500">En İyi %95</p>
                <p className="mt-2 text-2xl font-bold text-slate-950">
                  {monteCarloResult ? monteCarloResult.best_case.toFixed(2) : '-'}
                </p>
              </div>
            </div>

            <div className="mt-6 h-[380px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 12, right: 8, left: 0, bottom: 8 }}>
                  <CartesianGrid stroke="#dbe4f0" strokeDasharray="4 4" />
                  <XAxis dataKey="day" tick={{ fill: '#475569', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#475569', fontSize: 12 }} />
                  <Tooltip />
                  <Legend />
                  {Array.from({ length: Math.min(20, monteCarloResult?.all_simulations?.length ?? 0) }, (_, index) => (
                    <Line
                      key={`sim_${index + 1}`}
                      type="monotone"
                      dataKey={`sim_${index + 1}`}
                      stroke={index === 0 ? '#0f172a' : '#94a3b8'}
                      strokeWidth={index === 0 ? 2.5 : 1.2}
                      dot={false}
                      name={`Sim ${index + 1}`}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>
      </section>
    </div>
  )
}

export default AnalysisPage
