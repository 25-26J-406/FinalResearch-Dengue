const DistrictTable = ({ districts }) => {
  const getRiskBadgeColor = (risk) => {
    const colors = {
      High: 'bg-red-100 text-red-800',
      Medium: 'bg-yellow-100 text-yellow-800',
      Low: 'bg-green-100 text-green-800',
    };
    return colors[risk] || 'bg-gray-100 text-gray-800';
  };

  if (!districts || districts.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        No hotspots detected
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              District
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Risk Level
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Priority Score
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Recommended Resources
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {districts.map((district, idx) => (
            <tr key={idx} className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm font-medium text-gray-900">
                {district.District}
              </td>
              <td className="px-6 py-4">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskBadgeColor(district.Risk_Level)}`}>
                  {district.Risk_Level}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-gray-900">
                {district.Hotspot_Priority?.toFixed(3) || 'N/A'}
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                <div className="flex gap-2 flex-wrap">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-50 text-blue-700">
                    🚿 {district.Fogging_Units}
                  </span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-50 text-green-700">
                    👤 {district.Health_Inspectors}
                  </span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-50 text-purple-700">
                    👥 {district.Inspection_Teams}
                  </span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-orange-50 text-orange-700">
                    🏥 {district.Treatment_Units}
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DistrictTable;