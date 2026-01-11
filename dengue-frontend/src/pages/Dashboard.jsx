import { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  TrendingUp, 
  Users, 
  Activity 
} from 'lucide-react';
import { adminAPI, predictionsAPI } from '../services/api';
import StatsCard from '../components/dashboard/StatsCard';
import RiskDistributionChart from '../components/dashboard/RiskDistributionChart';
import ResourceGapChart from '../components/dashboard/ResourceGapChart';
import DistrictTable from '../components/dashboard/DistrictTable';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overview, setOverview] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [hotspots, setHotspots] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const overviewRes = await adminAPI.getOverview();
      
      setOverview(overviewRes.data);
      setStatistics(overviewRes.data.summary);
      setHotspots(overviewRes.data.hotspots || []);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  if (error) {
    return <ErrorAlert message={error} onRetry={fetchDashboardData} />;
  }

  const summary = overview?.summary || {};
  const stats = summary;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-1">
          Real-time overview of dengue risk and resource allocation
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Districts"
          value={summary.total_districts || 0}
          icon={Activity}
          color="blue"
          trend={null}
        />
        <StatsCard
          title="High Risk Districts"
          value={summary.high_risk_count || 0}
          icon={AlertTriangle}
          color="red"
          trend={null}
        />
        <StatsCard
          title="Medium Risk"
          value={summary.medium_risk_count || 0}
          icon={TrendingUp}
          color="yellow"
          trend={null}
        />
        <StatsCard
          title="Low Risk"
          value={summary.low_risk_count || 0}
          icon={Users}
          color="green"
          trend={null}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskDistributionChart data={summary} />
        <ResourceGapChart data={overview} />
      </div>

      {/* Hotspots Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            High-Risk Districts (Hotspots)
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Districts requiring immediate attention
          </p>
        </div>
        <DistrictTable districts={hotspots} />
      </div>

      {/* Statistics Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          System Statistics
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">Total Districts</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {summary.total_districts || 0}
            </p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">Hotspot Count</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {summary.hotspot_count || 0}
            </p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">Hotspot Rate</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {summary.total_districts ? ((summary.hotspot_count / summary.total_districts) * 100).toFixed(1) : 0}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;