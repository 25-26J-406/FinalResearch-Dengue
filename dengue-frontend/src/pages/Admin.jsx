import { useState, useEffect } from 'react';
import { 
  Activity, 
  TrendingUp, 
  Users, 
  Package,
  Download,
  BarChart3
} from 'lucide-react';
import { adminAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Admin = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overview, setOverview] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [resourceGap, setResourceGap] = useState(null);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [overviewRes, statsRes, gapRes] = await Promise.all([
        adminAPI.getOverview(),
        adminAPI.getStatistics(),
        adminAPI.getResourceGap(),
      ]);
      
      setOverview(overviewRes.data);
      setStatistics(statsRes.data);
      setResourceGap(gapRes.data);
    } catch (err) {
      setError(err.message || 'Failed to load admin data');
      console.error('Admin error:', err);
    } finally {
      setLoading(false);
    }
  };

  const exportData = () => {
    const data = {
      overview,
      statistics,
      resourceGap,
      exportedAt: new Date().toISOString(),
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dengue-admin-report-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <LoadingSpinner message="Loading admin panel..." />;
  }

  if (error) {
    return <ErrorAlert message={error} onRetry={fetchAdminData} />;
  }

  const summary = overview?.summary || {};
  const stats = statistics?.statistics || {};

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Admin Dashboard</h2>
          <p className="text-gray-600 mt-1">
            Complete system overview and analytics
          </p>
        </div>
        <button
          onClick={exportData}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Download className="w-4 h-4" />
          Export Report
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-blue-50">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {summary.total_districts || 0}
          </h3>
          <p className="text-sm text-gray-600">Total Districts</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-red-50">
              <TrendingUp className="w-6 h-6 text-red-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {stats.avg_cases_per_district?.toFixed(0) || 0}
          </h3>
          <p className="text-sm text-gray-600">Avg Cases/District</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-green-50">
              <Users className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {((stats.avg_population_per_district || 0) / 1000).toFixed(0)}K
          </h3>
          <p className="text-sm text-gray-600">Avg Population</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-purple-50">
              <Package className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {stats.resource_allocation_efficiency?.toFixed(1) || 0}%
          </h3>
          <p className="text-sm text-gray-600">Resource Efficiency</p>
        </div>
      </div>

      {/* Resource Gap Analysis */}
      {resourceGap && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Resource Gap Analysis
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(resourceGap.resource_summary || {}).map(([key, value]) => (
              <div key={key} className="p-4 border border-gray-200 rounded-lg">
                <h4 className="text-sm font-medium text-gray-600 mb-3">
                  {key.replace(/_/g, ' ')}
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Available:</span>
                    <span className="font-semibold text-green-600">{value.available}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Needed:</span>
                    <span className="font-semibold text-blue-600">{value.needed}</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-gray-200">
                    <span className="text-gray-600">Gap:</span>
                    <span className={`font-bold ${value.gap > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {value.gap > 0 ? `+${value.gap}` : value.gap}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Risk Distribution
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
              <div>
                <p className="text-sm text-red-600 font-medium">High Risk Districts</p>
                <p className="text-2xl font-bold text-red-900 mt-1">
                  {summary.high_risk_count || 0}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-red-600">Percentage</p>
                <p className="text-xl font-bold text-red-900">
                  {stats.hotspot_percentage?.toFixed(1) || 0}%
                </p>
              </div>
            </div>
            <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
              <div>
                <p className="text-sm text-yellow-600 font-medium">Medium Risk Districts</p>
                <p className="text-2xl font-bold text-yellow-900 mt-1">
                  {summary.medium_risk_count || 0}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-yellow-600">Percentage</p>
                <p className="text-xl font-bold text-yellow-900">
                  {((summary.medium_risk_count / summary.total_districts) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <div>
                <p className="text-sm text-green-600 font-medium">Low Risk Districts</p>
                <p className="text-2xl font-bold text-green-900 mt-1">
                  {summary.low_risk_count || 0}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-green-600">Percentage</p>
                <p className="text-xl font-bold text-green-900">
                  {((summary.low_risk_count / summary.total_districts) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            System Health
          </h3>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-blue-600 font-medium">Data Quality</span>
                <span className="text-xl font-bold text-blue-900">98%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '98%' }}></div>
              </div>
            </div>
            
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-green-600 font-medium">Prediction Accuracy</span>
                <span className="text-xl font-bold text-green-900">
                  {stats.avg_confidence?.toFixed(1) || 0}%
                </span>
              </div>
              <div className="w-full bg-green-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: `${stats.avg_confidence || 0}%` }}></div>
              </div>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-purple-600 font-medium">Resource Utilization</span>
                <span className="text-xl font-bold text-purple-900">
                  {stats.resource_allocation_efficiency?.toFixed(1) || 0}%
                </span>
              </div>
              <div className="w-full bg-purple-200 rounded-full h-2">
                <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${stats.resource_allocation_efficiency || 0}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Districts Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            All Districts Overview
          </h3>
        </div>
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
                  Population
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Cases
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Cases/1000
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {overview?.districts?.map((district, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {district.district}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      district.risk_level === 'High' ? 'bg-red-100 text-red-800' :
                      district.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {district.risk_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {(district.population / 1000).toFixed(0)}K
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {district.cases}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {district.cases_per_1000?.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Admin;