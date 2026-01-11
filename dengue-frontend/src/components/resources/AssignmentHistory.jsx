import { format } from 'date-fns';

const AssignmentHistory = ({ assignments }) => {
  if (!assignments || assignments.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Assignment History
        </h3>
        <p className="text-gray-500 text-center py-8">
          No assignments yet
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Assignment History
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                District
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Fogging
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Inspectors
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Teams
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Treatment
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Date
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {assignments.map((assignment, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                  {assignment.district}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {assignment.resources.Fogging_Units}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {assignment.resources.Health_Inspectors}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {assignment.resources.Inspection_Teams}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {assignment.resources.Treatment_Units}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {assignment.assigned_at ? format(new Date(assignment.assigned_at), 'MMM dd, yyyy HH:mm') : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AssignmentHistory;