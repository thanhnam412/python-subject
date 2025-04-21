"use client";

import * as React from "react";
import {
  AudioWaveform,
  Command,
  GalleryVerticalEnd,
  Map,
  ChartNoAxesGantt,
  Plus,
} from "lucide-react";

import { NavMain } from "@/components/nav-main";
import { NavProjects } from "@/components/nav-projects";
import { NavUser } from "@/components/nav-user";
import { TeamSwitcher } from "@/components/team-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";

const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  teams: [
    {
      name: "Acme Inc",
      logo: GalleryVerticalEnd,
      plan: "Enterprise",
    },
    {
      name: "Acme Corp.",
      logo: AudioWaveform,
      plan: "Startup",
    },
    {
      name: "Evil Corp.",
      logo: Command,
      plan: "Free",
    },
  ],
  navMain: [
    {
      title: "Thêm mới",
      url: "/dashboard/add",
      icon: Plus,
      isActive: true,
      items: [
        {
          title: "Thu Nhập",
          url: "/dashboard/add/income",
        },
        {
          title: "Chi tiêu",
          url: "/dashboard/add/expense",
        },
        {
          title: "Khoản nợ",
          url: "/dashboard/add/loan",
        },
      ],
    },
  ],
  projects: [
    {
      name: "Tổng quan",
      url: "/dashboard/overview",
      icon: ChartNoAxesGantt,
    },
    {
      name: "Cá nhân",
      url: "/dashboard/personal",
      icon: Map,
    },
  ],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
