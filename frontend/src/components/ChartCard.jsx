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
import { formatCurrency } from '../utils/formatters'

function ChartCard({ data, title, description }) {
  return (
    <section className="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-soft">
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-slate-950">{title}</h3>
        <p className="mt-2 text-sm text-slate-600">{description}</p>
      </div>

      <div className="h-[360px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 12, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid stroke="#dbe4f0" strokeDasharray="4 4" />
            <XAxis dataKey="date" tick={{ fill: '#475569', fontSize: 12 }} />
            <YAxis tick={{ fill: '#475569', fontSize: 12 }} />
            <Tooltip
              formatter={(value) => formatCurrency(value)}
              labelFormatter={(label) => `Tarih: ${label}`}
              contentStyle={{
                borderRadius: '16px',
                border: '1px solid #e2e8f0',
                boxShadow: '0 18px 45px rgba(15, 23, 42, 0.12)',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="XAU"
              name="Altın"
              stroke="#d4a017"
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="XAG"
              name="Gümüş"
              stroke="#64748b"
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}

export default ChartCard
