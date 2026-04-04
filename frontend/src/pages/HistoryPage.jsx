import { useEffect, useState } from 'react'
import ChartCard from '../components/ChartCard'
import SectionHeader from '../components/SectionHeader'
import { metalsApi } from '../services/api'
import { buildHistoryChartData } from '../utils/formatters'

function HistoryPage() {
  const [chartData, setChartData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchHistory() {
      try {
        setLoading(true)
        const response = await metalsApi.getAllPrices()
        setChartData(buildHistoryChartData(response.data))
        setError('')
      } catch {
        setError('Fiyat geçmişi alınamadı. API erişimini kontrol edin.')
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [])

  return (
    <div className="space-y-8">
      <SectionHeader
        eyebrow="Fiyat Geçmişi"
        title="Altın ve gümüş fiyatlarını çizgi grafik üzerinde incele"
        description="Recharts ile oluşturulan grafik, API'den gelen tarihsel kayıtları tek bir zaman ekseninde birleştirir ve iki madeni karşılaştırmalı olarak gösterir."
      />

      {error && <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-rose-700">{error}</div>}

      {loading ? (
        <div className="rounded-3xl border border-slate-200 bg-white/80 p-8 text-slate-600 shadow-soft">
          Grafik verileri yükleniyor...
        </div>
      ) : (
        <ChartCard
          data={chartData}
          title="Metal Fiyatlarının Tarihsel Seyri"
          description="X ekseni tarih, Y ekseni TL bazlı fiyatı gösterir. Altın ve gümüş verileri aynı grafikte karşılaştırılır."
        />
      )}
    </div>
  )
}

export default HistoryPage
