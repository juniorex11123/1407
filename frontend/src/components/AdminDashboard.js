import React, { useState, useEffect } from 'react';
import { employeesAPI, timeEntriesAPI, usersAPI } from '../services/api';

function AdminDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('employees');
  const [employees, setEmployees] = useState([]);
  const [timeReports, setTimeReports] = useState([]);
  const [users, setUsers] = useState([]);
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

  // User management state
  const [showUserModal, setShowUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [userForm, setUserForm] = useState({
    username: '',
    password: '',
    type: 'user'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load company info from user data
      if (user.company_id && user.company_name) {
        setCompanyInfo({ id: user.company_id, name: user.company_name });
      }

      // Load employees, time reports, and users
      const [employeesData, timeEntriesData, usersData] = await Promise.all([
        employeesAPI.getAll(),
        timeEntriesAPI.getAll(),
        usersAPI.getAll()
      ]);

      setEmployees(employeesData);
      setTimeReports(timeEntriesData);
      setUsers(usersData);

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

  // Time Entry Management
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
        setError('Błąd podczas usuwania wpisu');
      }
    }
  };

  // User Management
  const handleCreateUser = () => {
    setEditingUser(null);
    setUserForm({
      username: '',
      password: '',
      type: 'user'
    });
    setShowUserModal(true);
  };

  const handleEditUser = (userToEdit) => {
    setEditingUser(userToEdit);
    setUserForm({
      username: userToEdit.username,
      password: '',
      type: userToEdit.type
    });
    setShowUserModal(true);
  };

  const handleUserSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        // Update user
        const updateData = { ...userForm };
        if (!updateData.password) {
          delete updateData.password; // Don't update password if empty
        }
        await usersAPI.update(editingUser.id, updateData);
      } else {
        // Create user
        await usersAPI.create(userForm);
      }
      setShowUserModal(false);
      await loadData();
    } catch (error) {
      console.error('Error saving user:', error);
      setError('Błąd podczas zapisywania użytkownika');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Czy na pewno chcesz usunąć tego użytkownika?')) {
      try {
        await usersAPI.delete(userId);
        await loadData();
      } catch (error) {
        console.error('Error deleting user:', error);
        setError('Błąd podczas usuwania użytkownika');
      }
    }
  };

  // Get employee name by ID
  const getEmployeeName = (employeeId) => {
    const employee = employees.find(emp => emp.id === employeeId);
    return employee ? employee.name : 'Nieznany pracownik';
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
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Panel Administratora</h1>
              <p className="mt-1 text-sm text-gray-500">
                Witaj, {user.username} | {companyInfo?.name}
              </p>
            </div>
            <button
              onClick={onLogout}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition duration-200"
            >
              Wyloguj
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('employees')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'employees'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Pracownicy
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'reports'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Raporty czasu
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'users'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Użytkownicy
            </button>
          </nav>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'employees' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Lista pracowników</h2>
            </div>
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                {employees.length === 0 ? (
                  <p className="text-gray-500">Brak pracowników</p>
                ) : (
                  <div className="space-y-4">
                    {employees.map(employee => (
                      <div key={employee.id} className="flex items-center justify-between border-b pb-4">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">{employee.name}</h3>
                          <p className="text-sm text-gray-500">Kod QR: {employee.qr_code}</p>
                          <p className="text-sm text-gray-500">
                            Status: {employee.is_active ? 'Aktywny' : 'Nieaktywny'}
                          </p>
                        </div>
                        <button
                          onClick={() => generateQRCode(employee)}
                          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                        >
                          Generuj QR
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Raporty czasu pracy</h2>
            </div>
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                {timeReports.length === 0 ? (
                  <p className="text-gray-500">Brak raportów</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Pracownik
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Data
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Wejście
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Wyjście
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Godziny
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Akcje
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {timeReports.map(report => (
                          <tr key={report.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {getEmployeeName(report.employee_id)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {report.date}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {report.check_in ? new Date(report.check_in).toLocaleTimeString() : '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {report.check_out ? new Date(report.check_out).toLocaleTimeString() : '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {report.total_hours ? `${report.total_hours.toFixed(1)}h` : '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                              <button
                                onClick={() => handleEditTimeEntry(report)}
                                className="text-blue-600 hover:text-blue-900"
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
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Zarządzanie użytkownikami</h2>
              <button
                onClick={handleCreateUser}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                Dodaj użytkownika
              </button>
            </div>
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                {users.length === 0 ? (
                  <p className="text-gray-500">Brak użytkowników</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Nazwa użytkownika
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Typ
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Data utworzenia
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Akcje
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {users.map(userItem => (
                          <tr key={userItem.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {userItem.username}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                userItem.type === 'admin' ? 'bg-purple-100 text-purple-800' :
                                userItem.type === 'owner' ? 'bg-red-100 text-red-800' :
                                'bg-green-100 text-green-800'
                              }`}>
                                {userItem.type}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {new Date(userItem.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                              {userItem.type === 'user' && (
                                <>
                                  <button
                                    onClick={() => handleEditUser(userItem)}
                                    className="text-blue-600 hover:text-blue-900"
                                  >
                                    Edytuj
                                  </button>
                                  <button
                                    onClick={() => handleDeleteUser(userItem.id)}
                                    className="text-red-600 hover:text-red-900"
                                  >
                                    Usuń
                                  </button>
                                </>
                              )}
                              {userItem.type !== 'user' && (
                                <span className="text-gray-400">
                                  {userItem.type === 'admin' ? 'Nie można edytować admina' : 'Nie można edytować właściciela'}
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* QR Code Modal */}
      {showQRModal && selectedEmployee && qrCodeData && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Kod QR dla {selectedEmployee.name}</h2>
            <div className="text-center">
              <img 
                src={`data:image/png;base64,${qrCodeData.qr_code_image}`}
                alt="QR Code"
                className="mx-auto mb-4"
              />
              <p className="text-sm text-gray-600 mb-4">Kod: {qrCodeData.qr_code_data}</p>
              <button
                onClick={() => setShowQRModal(false)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Zamknij
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Time Entry Edit Modal */}
      {showTimeEntryModal && editingTimeEntry && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">
              Edytuj wpis czasu - {getEmployeeName(editingTimeEntry.employee_id)}
            </h2>
            <form onSubmit={handleTimeEntrySubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Godzina wejścia
                </label>
                <input
                  type="datetime-local"
                  value={timeEntryForm.check_in}
                  onChange={(e) => setTimeEntryForm({...timeEntryForm, check_in: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Godzina wyjścia
                </label>
                <input
                  type="datetime-local"
                  value={timeEntryForm.check_out}
                  onChange={(e) => setTimeEntryForm({...timeEntryForm, check_out: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                >
                  Zapisz
                </button>
                <button
                  type="button"
                  onClick={() => setShowTimeEntryModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                >
                  Anuluj
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* User Create/Edit Modal */}
      {showUserModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">
              {editingUser ? 'Edytuj użytkownika' : 'Dodaj nowego użytkownika'}
            </h2>
            <form onSubmit={handleUserSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nazwa użytkownika
                </label>
                <input
                  type="text"
                  value={userForm.username}
                  onChange={(e) => setUserForm({...userForm, username: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hasło {editingUser && '(pozostaw puste aby nie zmieniać)'}
                </label>
                <input
                  type="password"
                  value={userForm.password}
                  onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required={!editingUser}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Typ użytkownika
                </label>
                <select
                  value={userForm.type}
                  onChange={(e) => setUserForm({...userForm, type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="user">Użytkownik</option>
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Administratorzy mogą tworzyć tylko użytkowników typu "user"
                </p>
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                >
                  {editingUser ? 'Aktualizuj' : 'Dodaj'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUserModal(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                >
                  Anuluj
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;