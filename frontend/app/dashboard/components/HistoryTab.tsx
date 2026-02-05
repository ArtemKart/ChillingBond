const purchaseHistory = [
  {
    id: '1',
    series: 'BOND-2024-A',
    quantity: 50,
    faceValue: 1000,
    purchaseDate: '2024-01-15',
    totalValue: 50000,
    paymentExpired: false,
  },
  {
    id: '2',
    series: 'BOND-2024-B',
    quantity: 100,
    faceValue: 500,
    purchaseDate: '2024-02-20',
    totalValue: 50000,
    paymentExpired: false,
  },
  {
    id: '3',
    series: 'BOND-2023-C',
    quantity: 25,
    faceValue: 2000,
    purchaseDate: '2023-11-10',
    totalValue: 50000,
    paymentExpired: true,
  },
  {
    id: '4',
    series: 'BOND-2024-D',
    quantity: 75,
    faceValue: 750,
    purchaseDate: '2024-03-05',
    totalValue: 56250,
    paymentExpired: false,
  },
  {
    id: '5',
    series: 'BOND-2023-E',
    quantity: 40,
    faceValue: 1500,
    purchaseDate: '2023-09-18',
    totalValue: 60000,
    paymentExpired: true,
  },
];

export function HistoryTab() {
  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">Purchase History</h2>
      
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900">All Purchases</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Series
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Face Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Purchase Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Payment Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {purchaseHistory.map((purchase) => (
                <tr key={purchase.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{purchase.series}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{purchase.quantity}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">${purchase.faceValue.toLocaleString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">${purchase.totalValue.toLocaleString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {purchase.purchaseDate}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      purchase.paymentExpired 
                        ? 'bg-red-100 text-red-700' 
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {purchase.paymentExpired ? 'Expired' : 'Active'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
