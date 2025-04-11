"use client";

import { ReactNode } from "react";

interface ProviderProps {
  children: ReactNode;
}

const Providers = ({ children }: ProviderProps) => {
  return <div>{children}</div>;
};

export default Providers;
