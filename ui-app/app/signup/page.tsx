import { SignUpForm } from "@/components/sign-form";

const Icon = {
  wallet: () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="40"
      height="40"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    >
      <path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1" />
      <path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4" />
    </svg>
  ),
};

const SignUp = () => {
  return (
    <div className="h-screen w-screen p-[100px]">
      <div className="flex items-center gap-[12px] text-[#299D91] text-[30px] font-semibold">
        <Icon.wallet />
        <h1>QUẢN LÝ CHI TIÊU</h1>
      </div>
      <div className="w-full flex justify-center">
        <SignUpForm className="col-span-5 h-full flex flex-col justify-center p-[100px] min-w-[600px] max-w-[700px]" />
      </div>
    </div>
  );
};

export default SignUp;
