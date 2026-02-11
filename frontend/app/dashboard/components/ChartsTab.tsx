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
import { api } from "@/lib/api";
import { useEffect, useState } from "react";

interface EquityDataPoint {
    date: string;
    totalValue: number;
}

interface EquityResponse {
    equity: [string, string][];
}


export function ChartsTab() {
    const [portfolioData, setPortfolioData] = useState<EquityDataPoint[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchEquityData = async () => {
            try {
                setIsLoading(true);
                setError(null);

                const response =
                    await api.get<EquityResponse>("/data/equity");

                const transformedData: EquityDataPoint[] = response.equity.map(
                    ([date, value]) => ({
                        date,
                        totalValue: parseFloat(value),
                    }),
                );

                setPortfolioData(transformedData);
            } catch (err) {
                console.error("Failed to fetch equity data:", err);
                setError("Failed to load portfolio data");
            } finally {
                setIsLoading(false);
            }
        };

        fetchEquityData();
    }, []);

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

                    {isLoading ? (
                        <div className="flex items-center justify-center h-[350px]">
                            <div className="text-center">
                                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
                                <p className="mt-2 text-sm text-gray-500">
                                    Loading data...
                                </p>
                            </div>
                        </div>
                    ) : error ? (
                        <div className="flex items-center justify-center h-[350px]">
                            <div className="text-center">
                                <p className="text-red-600 font-medium">
                                    {error}
                                </p>
                                <button
                                    onClick={() => window.location.reload()}
                                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    Retry
                                </button>
                            </div>
                        </div>
                    ) : portfolioData.length === 0 ? (
                        <div className="flex items-center justify-center h-[350px] text-gray-400">
                            <p>No data available</p>
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height={350}>
                            <LineChart data={portfolioData}>
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
                                        `${value.toLocaleString()} PLN`
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
                    )}
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
