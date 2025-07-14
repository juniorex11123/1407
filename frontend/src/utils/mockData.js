export const mockData = {
  users: [
    {
      id: 1,
      username: 'owner',
      password: 'owner123',
      type: 'owner',
      role: 'owner',
      company_id: null,
      company_name: 'System Owner'
    },
    {
      id: 2,
      username: 'admin',
      password: 'admin123',
      type: 'admin',
      role: 'admin',
      company_id: 1,
      company_name: 'Firma ABC'
    },
    {
      id: 3,
      username: 'user',
      password: 'user123',
      type: 'user',
      role: 'user',
      company_id: 1,
      company_name: 'Firma ABC'
    }
  ],
  
  companies: [
    {
      id: 1,
      name: 'Firma ABC',
      created_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 2,
      name: 'Firma XYZ',
      created_at: '2024-01-01T00:00:00Z'
    }
  ],
  
  employees: [
    {
      id: 1,
      name: 'Jan Kowalski',
      qr_code: 'QR-EMP-001',
      company_id: 1,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 2,
      name: 'Anna Nowak',
      qr_code: 'QR-EMP-002',
      company_id: 1,
      is_active: true,
      created_at: '2024-01-01T00:00:00Z'
    }
  ],
  
  timeEntries: [
    {
      id: 1,
      employee_id: 1,
      check_in: '2024-01-15T08:00:00Z',
      check_out: '2024-01-15T16:00:00Z',
      date: '2024-01-15',
      total_hours: 8.0
    },
    {
      id: 2,
      employee_id: 2,
      check_in: '2024-01-15T09:00:00Z',
      check_out: '2024-01-15T17:00:00Z',
      date: '2024-01-15',
      total_hours: 8.0
    }
  ]
};