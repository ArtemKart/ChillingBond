"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";
import {
    Clock,
    DollarSign,
    Info,
    X,
} from "lucide-react";

interface AddBondModalProps {
    onClose: () => void;
    onUpdate?: () => void;
}

type BondCreatePayload = {
    series: string;
    nominal_value: number;
    quantity: number;
    purchase_date: string;
    initial_interest_rate: number;
    reference_rate_margin: number;
    first_interest_period: number;
    maturity_period: number;
};

export default function AddBondModal({ onClose, onUpdate }: AddBondModalProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [formData, setFormData] = useState({
        series: "",
        nominalValue: "",
        quantity: 1,
        purchaseDate: new Date().toISOString().split("T")[0],

        initialInterestRate: "",
        referenceRateMargin: 0,
        firstInterestPeriod: 0,

        maturityPeriod: "",
    });

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
    ) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const payload: BondCreatePayload = {
                series: formData.series.trim(),
                nominal_value: Number(formData.nominalValue),
                quantity: Number(formData.quantity),
                purchase_date: formData.purchaseDate,
                initial_interest_rate: Number(formData.initialInterestRate),
                reference_rate_margin: Number(formData.referenceRateMargin),
                first_interest_period: Number(formData.firstInterestPeriod),
                maturity_period: Number(formData.maturityPeriod),
            };

            await apiFetch("/bonds", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            if (onUpdate) {
                onUpdate();
            }
            onClose();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Error Adding Item");
        } finally {
            setLoading(false);
        }
    };
    return (
        <div
            className="fixed inset-0 flex items-center justify-center z-50 p-4 backdrop-blur-sm bg-black/10"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-2xl font-semibold text-gray-900">
                        Add New Bondholder
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                    >
                        <X className="size-5" />
                    </button>
                </div>

                {/* Content */}
                <form onSubmit={handleSubmit} className="p-6">
                    <div className="space-y-6">
                        {/* Bond Information */}
                        <div className="border-t border-gray-200 pt-6">
                            <h3 className="font-semibold text-gray-900 mb-4">
                                <div className="flex items-center gap-2">
                                    <Info className="size-4" />
                                    Bond Information
                                </div>
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Bond Series
                                    </label>
                                    <input
                                        type="text"
                                        name="series"
                                        placeholder="Enter Bond series"
                                        value={formData.series}
                                        onChange={handleChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Quantity
                                    </label>
                                    <input
                                        type="number"
                                        name="quantity"
                                        value={formData.quantity}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                                        placeholder="0"
                                        min="1"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Purchase Date
                                    </label>
                                    <input
                                        type="date"
                                        name="purchaseDate"
                                        value={formData.purchaseDate}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Financial Information */}
                        <div className="border-t border-gray-200 pt-6">
                            <h3 className="font-semibold text-gray-900 mb-4">
                                <div className="flex items-center gap-2">
                                    <DollarSign className="size-4" />
                                    Financial Information
                                </div>
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Face Value
                                    </label>
                                    <input
                                        type="number"
                                        name="nominalValue"
                                        value={formData.nominalValue}
                                        onChange={handleChange}
                                        min="1"
                                        placeholder="0"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Initial Interest Rate
                                    </label>
                                    <input
                                        type="number"
                                        step={0.01}
                                        name="initialInterestRate"
                                        value={formData.initialInterestRate}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                                        placeholder="0"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Rate Margin
                                    </label>
                                    <input
                                        type="number"
                                        step={0.01}
                                        placeholder="0"
                                        name="referenceRateMargin"
                                        value={formData.referenceRateMargin}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Investment Terms */}
                        <div className="border-t border-gray-200 pt-6">
                            <h3 className="font-semibold text-gray-900 mb-4">
                                <div className="flex items-center gap-2">
                                    <Clock className="size-4" />
                                    Investment Terms
                                </div>
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        First Interest Period
                                    </label>
                                    <input
                                        type="number"
                                        name="firstInterestPeriod"
                                        value={formData.firstInterestPeriod}
                                        onChange={handleChange}
                                        placeholder="0"
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Maturity Period
                                    </label>
                                    <input
                                        type="number"
                                        step={0.01}
                                        name="maturityPeriod"
                                        value={formData.maturityPeriod}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                                        placeholder="0"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3 pt-4 border-t border-gray-200">
                            <button
                                type="button"
                                onClick={onClose}
                                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                            >
                                Add Bondholder
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
    return (
        <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={onClose}
            role="presentation"
        >
            <div
                className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden"
                onClick={(e) => e.stopPropagation()}
                role="dialog"
                aria-modal="true"
            >
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-gray-900">
                        Add bond
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {error && (
                        <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                            {error}
                        </div>
                    )}

                    <div className="space-y-4">
                        <div className="text-sm font-semibold text-gray-900">
                            Basic Information
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Series
                            </label>
                            <input
                                type="text"
                                required
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                value={formData.series}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        series: e.target.value,
                                    })
                                }
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Face value
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                required
                                min="0"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                value={formData.nominal_value}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        nominal_value: e.target.value,
                                    })
                                }
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Quantity
                            </label>
                            <input
                                type="number"
                                required
                                min="1"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                value={formData.quantity}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        quantity: parseInt(
                                            e.target.value || "1",
                                            10,
                                        ),
                                    })
                                }
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Purchase date
                            </label>
                            <input
                                type="date"
                                required
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                value={formData.purchase_date}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        purchase_date: e.target.value,
                                    })
                                }
                            />
                        </div>

                        <div className="text-sm font-semibold text-gray-900 pt-2">
                            Financial Parameters
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Initial Interest Rate
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                required
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                value={formData.initial_interest_rate}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        initial_interest_rate: e.target.value,
                                    })
                                }
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Rate Margin
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                required
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                value={formData.reference_rate_margin}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        reference_rate_margin: e.target.value,
                                    })
                                }
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                First Interest Period (mo)
                            </label>
                            <input
                                type="number"
                                required
                                min="1"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                value={formData.first_interest_period}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        first_interest_period: e.target.value,
                                    })
                                }
                            />
                        </div>

                        <div className="text-sm font-semibold text-gray-900 pt-2">
                            Time Parameters
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Maturity Period (mo)
                            </label>
                            <input
                                type="number"
                                required
                                min="1"
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-900"
                                value={formData.maturity_period}
                                onChange={(e) =>
                                    setFormData({
                                        ...formData,
                                        maturity_period: e.target.value,
                                    })
                                }
                            />
                        </div>
                    </div>

                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:bg-blue-400"
                        >
                            {loading ? "Adding..." : "Add"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
