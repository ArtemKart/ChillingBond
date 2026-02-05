import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";

// Placeholder data - replace with real data later
const portfolioValueData = [
    { date: "2024-01", totalValue: 150000 },
    { date: "2024-02", totalValue: 165000 },
    { date: "2024-03", totalValue: 180000 },
    { date: "2024-04", totalValue: 175000 },
    { date: "2024-05", totalValue: 195000 },
    { date: "2024-06", totalValue: 210000 },
];

const bondTypeData = [
    { type: "Type A", value: 80000 },
    { type: "Type B", value: 60000 },
    { type: "Type C", value: 45000 },
    { type: "Type D", value: 25000 },
];

export function ChartsTab() {
    return (
        <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                Analytics & Charts
            </h2>

            <div className="space-y-6">
                {/* Portfolio Value Over Time */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="font-semibold text-gray-900 mb-6">
                        Portfolio Value Over Time
                    </h3>
                    <ResponsiveContainer width="100%" height={350}>
                        <LineChart data={portfolioValueData}>
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#e5e7eb"
                            />
                            <XAxis
                                dataKey="date"
                                stroke="#6b7280"
                                fontSize={12}
                            />
                            <YAxis stroke="#6b7280" fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "white",
                                    border: "1px solid #e5e7eb",
                                    borderRadius: "0.5rem",
                                }}
                                formatter={(value: number) =>
                                    `$${value.toLocaleString()}`
                                }
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="totalValue"
                                name="Total Value"
                                stroke="#3b82f6"
                                strokeWidth={3}
                                dot={{ fill: "#3b82f6", r: 5 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Bonds by Type */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="font-semibold text-gray-900 mb-6">
                        Bonds by Type
                    </h3>
                    <ResponsiveContainer width="100%" height={350}>
                        <BarChart data={bondTypeData}>
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#e5e7eb"
                            />
                            <XAxis
                                dataKey="type"
                                stroke="#6b7280"
                                fontSize={12}
                            />
                            <YAxis stroke="#6b7280" fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "white",
                                    border: "1px solid #e5e7eb",
                                    borderRadius: "0.5rem",
                                }}
                                formatter={(value: number) =>
                                    `$${value.toLocaleString()}`
                                }
                            />
                            <Legend />
                            <Bar
                                dataKey="value"
                                name="Bond Value"
                                fill="#3b82f6"
                                radius={[8, 8, 0, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Placeholder for future charts */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center justify-center h-64 text-gray-400">
                        <div className="text-center">
                            <p className="text-lg font-medium">
                                Additional Charts
                            </p>
                            <p className="text-sm mt-2">
                                Placeholder for future analytics
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
