"use client";

import { BondsTab } from "@/app/dashboard/components/BondsTab";
import { ChartsTab } from "@/app/dashboard/components/ChartsTab";
import { HistoryTab } from "@/app/dashboard/components/HistoryTab";
import { Sidebar } from "@/app/dashboard/components/SideBar";
import { TabType } from "@/types/TabType";
import { useState } from "react";



export default function DashboardPage() {
    const [activeTab, setActiveTab] = useState<TabType>("bonds");

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="flex">
                <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
                <main className="flex-1 p-8">
                    {activeTab === "bonds" && <BondsTab />}
                    {activeTab === "charts" && <ChartsTab />}
                    {activeTab === "history" && <HistoryTab />}
                </main>
            </div>
        </div>
    );
}
