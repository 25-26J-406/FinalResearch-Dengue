import { useState, useEffect } from 'react';
import { Package, Send } from 'lucide-react';
import { resourcesAPI } from '../services/api';
import ResourceInventory from '../components/resources/ResourceInventory';
import ResourceAssignment from '../components/resources/ResourceAssignment';
import AssignmentHistory from '../components/resources/AssignmentHistory';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';
import SuccessAlert from '../components/common/SuccessAlert';

const Resources = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [resources, setResources] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [totalAllocated, setTotalAllocated] = useState(null);

  useEffect(() => {
    fetchResourceData();
  }, []);

  const fetchResourceData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [resourcesRes, assignmentsRes, allocatedRes] = await Promise.all([
        resourcesAPI.getResources(),
        resourcesAPI.getAssignments(),
        resourcesAPI.getTotalAllocated(),
      ]);
      console.log('Resource data:', resourcesRes.data, assignmentsRes.data, allocatedRes.data);
      setResources(resourcesRes.data.available_resources);
      setAssignments(assignmentsRes.data.assignments || []);
      setTotalAllocated(allocatedRes.data.total_allocated);
    } catch (err) {
      setError(err.message || 'Failed to load resource data');
      console.error('Resources error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateResources = async (updatedResources) => {
    try {
      setError(null);
      await resourcesAPI.updateResources(updatedResources);
      setSuccess('Resources updated successfully');
      setTimeout(() => setSuccess(null), 3000);
      await fetchResourceData();
    } catch (err) {
      setError(err.message || 'Failed to update resources');
    }
  };

  const handleAssignResources = async (assignment) => {
    try {
      setError(null);
      await resourcesAPI.assignResources(assignment);
      setSuccess(`Resources assigned to ${assignment.district} successfully`);
      setTimeout(() => setSuccess(null), 3000);
      await fetchResourceData();
    } catch (err) {
      setError(err.message || 'Failed to assign resources');
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading resources..." />;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Resource Management</h2>
        <p className="text-gray-600 mt-1">
          Manage and allocate resources across districts
        </p>
      </div>

      {/* Alerts */}
      {error && <ErrorAlert message={error} onClose={() => setError(null)} />}
      {success && <SuccessAlert message={success} onClose={() => setSuccess(null)} />}

      {/* Resource Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {resources && Object.entries(resources).map(([key, value]) => (
          <div key={key} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <Package className="w-8 h-8 text-blue-600" />
              <span className="text-3xl font-bold text-gray-900">{value}</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">
              {key.replace(/_/g, ' ')}
            </h3>
            {totalAllocated && (
              <p className="text-xs text-gray-500 mt-1">
                Allocated: {totalAllocated[key] || 0}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Resource Management Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ResourceInventory
          resources={resources}
          onUpdate={handleUpdateResources}
        />
        <ResourceAssignment
          availableResources={resources}
          onAssign={handleAssignResources}
        />
      </div>

      {/* Assignment History */}
      <AssignmentHistory assignments={assignments} />
    </div>
  );
};

export default Resources;