"use client";

import { BondsTab } from "@/app/dashboard/components/BondsTab";
import { ChartsTab } from "@/app/dashboard/components/ChartsTab";
import { Sidebar } from "@/app/dashboard/components/SideBar";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { TabType } from "@/types/TabType";
import { useState } from "react";

export default function DashboardPage() {
    const [activeTab, setActiveTab] = useState<TabType>("bonds");

    return (
        <ProtectedRoute>
            <div className="min-h-screen bg-gray-50">
                <div className="flex">
                    <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
                    <main className="flex-1 p-8">
                        {activeTab === "bonds" && <BondsTab />}
                        {activeTab === "charts" && <ChartsTab />}
                    </main>
                </div>
            </div>
        </ProtectedRoute>
    );
}
