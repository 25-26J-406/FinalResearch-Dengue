import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const RiskDistributionChart = ({ data }) => {
  const chartData = [
    { name: 'High Risk', value: data?.high_risk_count || 0, color: '#ef4444' },
    { name: 'Medium Risk', value: data?.medium_risk_count || 0, color: '#f59e0b' },
    { name: 'Low Risk', value: data?.low_risk_count || 0, color: '#10b981' },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Risk Distribution
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        {chartData.map((item) => (
          <div key={item.name} className="p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold" style={{ color: item.color }}>
              {item.value}
            </div>
            <div className="text-xs text-gray-600 mt-1">{item.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RiskDistributionChart;