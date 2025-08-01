import React, { useState, useEffect } from 'react';
import { employeesAPI, timeEntriesAPI } from '../services/api';

function AdminDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('employees');
  const [employees, setEmployees] = useState([]);
  const [timeReports, setTimeReports] = useState([]);
  const [companyInfo, setCompanyInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // QR Code modal state
  const [showQRModal, setShowQRModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [qrCodeData, setQRCodeData] = useState(null);

  // Time entry editing state
  const [showTimeEntryModal, setShowTimeEntryModal] = useState(false);
  const [editingTimeEntry, setEditingTimeEntry] = useState(null);
  const [timeEntryForm, setTimeEntryForm] = useState({
    check_in: '',
    check_out: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load company info from user data (admin can't access companies API)
      if (user.company_id && user.company_name) {
        setCompanyInfo({ id: user.company_id, name: user.company_name });
      }

      // Load employees and time reports
      const [employeesData, timeEntriesData] = await Promise.all([
        employeesAPI.getAll(),
        timeEntriesAPI.getAll()
      ]);

      setEmployees(employeesData);
      setTimeReports(timeEntriesData);

    } catch (error) {
      console.error('Error loading data:', error);
      setError('Błąd podczas ładowania danych');
    } finally {
      setLoading(false);
    }
  };

  const generateQRCode = async (employee) => {
    try {
      setError('');
      const qrData = await employeesAPI.generateQR(employee.id);
      setSelectedEmployee(employee);
      setQRCodeData(qrData);
      setShowQRModal(true);
    } catch (error) {
      console.error('Error generating QR code:', error);
      setError('Błąd podczas generowania kodu QR');
    }
  };

  const handleEditTimeEntry = (timeEntry) => {
    setEditingTimeEntry(timeEntry);
    setTimeEntryForm({
      check_in: timeEntry.check_in ? new Date(timeEntry.check_in).toISOString().slice(0, 16) : '',
      check_out: timeEntry.check_out ? new Date(timeEntry.check_out).toISOString().slice(0, 16) : ''
    });
    setShowTimeEntryModal(true);
  };

  const handleTimeEntrySubmit = async (e) => {
    e.preventDefault();
    try {
      const updateData = {
        check_in: timeEntryForm.check_in ? new Date(timeEntryForm.check_in).toISOString() : null,
        check_out: timeEntryForm.check_out ? new Date(timeEntryForm.check_out).toISOString() : null
      };
      
      await timeEntriesAPI.update(editingTimeEntry.id, updateData);
      setShowTimeEntryModal(false);
      await loadData();
    } catch (error) {
      console.error('Error updating time entry:', error);
      setError('Błąd podczas aktualizacji wpisu czasu');
    }
  };

  const handleDeleteTimeEntry = async (timeEntryId) => {
    if (window.confirm('Czy na pewno chcesz usunąć ten wpis czasu?')) {
      try {
        await timeEntriesAPI.delete(timeEntryId);
        await loadData();
      } catch (error) {
        console.error('Error deleting time entry:', error);
        setError('Błąd podczas usuwania wpisu czasu');
      }
    }
  };

  // Get employee name by ID
  const getEmployeeName = (employeeId) => {
    const employee = employees.find(e => e.id === employeeId);
    return employee ? employee.name : 'Nieznany';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-xl">Ładowanie...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Panel Administratora</h1>
              <div className="text-sm text-gray-600">
                <p>Witaj, {user.username}</p>
                {companyInfo && (
                  <p>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      🏢 {companyInfo.name}
                    </span>
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={onLogout}
              className="text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Wyloguj
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('employees')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'employees'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Pracownicy
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'reports'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Raporty czasu
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'employees' && (
          <div>
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-semibold text-gray-800">Lista pracowników</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Imię i nazwisko
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Kod QR
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Akcje
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {employees.map((employee) => (
                      <tr key={employee.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {employee.name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-500">
                            {employee.qr_code}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            employee.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {employee.is_active ? 'Aktywny' : 'Nieaktywny'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => generateQRCode(employee)}
                            className="text-blue-600 hover:text-blue-900 mr-4"
                          >
                            Generuj QR
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div>
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="px-6 py-4 border-b">
                <h2 className="text-lg font-semibold text-gray-800">Raporty czasu pracy</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Imię i nazwisko
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Data
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Przyjście
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Wyjście
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Godziny pracy
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Akcje
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {timeReports.map((report) => (
                      <tr key={report.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {getEmployeeName(report.employee_id)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(report.date).toLocaleDateString('pl-PL')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(report.check_in).toLocaleTimeString('pl-PL', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {report.check_out ? new Date(report.check_out).toLocaleTimeString('pl-PL', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          }) : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {report.total_hours || 0}h
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => handleEditTimeEntry(report)}
                            className="text-blue-600 hover:text-blue-900 mr-4"
                          >
                            Edytuj
                          </button>
                          <button
                            onClick={() => handleDeleteTimeEntry(report.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Usuń
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* QR Code Modal */}
      {showQRModal && selectedEmployee && qrCodeData && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Kod QR dla {selectedEmployee.name}
              </h3>
              <div className="mb-4">
                <img 
                  src={`data:image/png;base64,${qrCodeData.qr_code_image}`} 
                  alt="QR Code" 
                  className="mx-auto border rounded-lg"
                />
              </div>
              <div className="text-sm text-gray-600 mb-4">
                <p>Kod: <span className="font-mono font-bold">{qrCodeData.qr_code_data}</span></p>
              </div>
              <div className="flex justify-center">
                <button
                  onClick={() => setShowQRModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Zamknij
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Time Entry Edit Modal */}
      {showTimeEntryModal && editingTimeEntry && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Edytuj wpis czasu - {getEmployeeName(editingTimeEntry.employee_id)}
              </h3>
              <form onSubmit={handleTimeEntrySubmit}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Data: {new Date(editingTimeEntry.date).toLocaleDateString('pl-PL')}
                  </label>
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Przyjście
                  </label>
                  <input
                    type="datetime-local"
                    value={timeEntryForm.check_in}
                    onChange={(e) => setTimeEntryForm({ ...timeEntryForm, check_in: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Wyjście
                  </label>
                  <input
                    type="datetime-local"
                    value={timeEntryForm.check_out}
                    onChange={(e) => setTimeEntryForm({ ...timeEntryForm, check_out: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    type="button"
                    onClick={() => setShowTimeEntryModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                  >
                    Anuluj
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    Zaktualizuj
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;