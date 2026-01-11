import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ResourceGapChart = ({ data }) => {
  if (!data) return null;

  const resources = data.available_resources || {};
  const totals = data.resource_totals || {};

  const chartData = [
    {
      name: 'Fogging Units',
      Available: resources.Fogging_Units || 0,
      Needed: totals.Fogging_Units || 0,
    },
    {
      name: 'Inspectors',
      Available: resources.Health_Inspectors || 0,
      Needed: totals.Health_Inspectors || 0,
    },
    {
      name: 'Teams',
      Available: resources.Inspection_Teams || 0,
      Needed: totals.Inspection_Teams || 0,
    },
    {
      name: 'Treatment',
      Available: resources.Treatment_Units || 0,
      Needed: totals.Treatment_Units || 0,
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Resource Availability vs Needs
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="Available" fill="#10b981" name="Available" />
          <Bar dataKey="Needed" fill="#ef4444" name="Needed" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ResourceGapChart;