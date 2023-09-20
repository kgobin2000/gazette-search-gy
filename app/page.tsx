"use client";
import { FormEvent, useState } from "react";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { Pacifico } from 'next/font/google'

const pacifico = Pacifico({ weight: "400", subsets: ['latin'] })


export default function Home() {
  const [isLoading, setIsLoading] = useState<boolean>(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true); // Set loading to true when the request starts
  
    try {
      const formData = new FormData(event.currentTarget);
       await fetch("/api/search", {
        method: "POST",
        body: formData,
      });
      // Immediately show a toast notification
      toast.success("Submitted. You will receive an email with the results.");
    } catch (error: any) {
      // If an exception is thrown before the fetch, show an error toast
      toast.error(`An error occurred: ${error.message}`);
    } finally {
      setIsLoading(false); // Set loading to false
    }
  }
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-100">
         <h1 className={`${pacifico.className} text-5xl mb-8 text-center`}>Gazette Search GY</h1>
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <p className="mb-10 text-center text-lg">
          Search for your name in the official gazette&nbsp;
        </p>
      </div>

      <div className="flex flex-col items-center justify-center w-full">
        <form className="flex flex-col gap-4 font-mono" onSubmit={onSubmit}>
          <input
            type="text"
            name="name"
            placeholder="Enter your name"
            className="p-2 border rounded focus:ring focus:ring-opacity-50 focus:ring-gray-300 text-center"
          />
          <input
            type="number"
            placeholder="Enter year"
            name="year"
            className="p-2 border rounded focus:ring focus:ring-opacity-50 focus:ring-gray-300 text-center"
          />
          <input
            type="text"
            name="email"
            placeholder="Enter your email"
            className="p-2 border rounded focus:ring focus:ring-opacity-50 focus:ring-gray-300 text-center"
          />
          <button
            type="submit"
            className="text-gray-700 p-2 rounded hover:bg-gray-200 focus:outline-none focus:border-gray-300 focus:ring focus:ring-gray-200 bg-opacity-50"
            disabled={isLoading}
          >
            Search
          </button>
          <ToastContainer />
        </form>
      </div>

      <div className="mt-10">
  <div className="flex place-items-center gap-2 p-8">
    By{" "}
    <span className="font-bold text-lg">
      Astrasoft Labs.
    </span>
  </div>
</div>
    </main>
  );
}
