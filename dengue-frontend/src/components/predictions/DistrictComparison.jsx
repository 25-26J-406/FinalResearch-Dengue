import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { X } from 'lucide-react';

const DistrictComparisonCorrected = ({ districts, onRemove }) => {
  const chartData = districts.map(d => ({
    name: d.District,
    'Risk Score': d.Risk_Score || 0,
    'High Prob %': parseFloat(((d.High_Probability || 0) * 100).toFixed(1)),
    'Priority': parseFloat((d.Hotspot_Priority || 0).toFixed(3)) * 100,
  }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          District Comparison
        </h3>
        <div className="flex gap-2 flex-wrap">
          {districts.map((district) => (
            <button
              key={district.District}
              onClick={() => onRemove(district)}
              className="flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
            >
              {district.District}
              <X className="w-3 h-3" />
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="Risk Score" fill="#3b82f6" />
          <Bar dataKey="High Prob %" fill="#ef4444" />
          <Bar dataKey="Priority" fill="#f59e0b" />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {districts.map((district) => (
          <div key={district.District} className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">{district.District}</h4>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Risk:</span>
                <span className="font-medium">{district.Risk_Level}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Score:</span>
                <span className="font-medium">{district.Risk_Score}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Hotspot:</span>
                <span className="font-medium">{district.Is_Hotspot ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DistrictComparisonCorrected;