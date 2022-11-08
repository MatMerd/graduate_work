import React, { FC } from "react";
import { Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import axios from "axios";
import { ToastContainer, toast, Flip } from "react-toastify";
import { useNavigate } from "react-router-dom";
import "react-toastify/dist/ReactToastify.min.css";

const Login: FC = (): JSX.Element => {
    const navigate = useNavigate();
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm();
    const login = (data: any) => {
        let params = {
            login: data.login,
            password: data.password,
        };
        axios
            .post("http://127.0.0.1:8080/api/v1/login", data=params)
            .then(function (response) {
                if (response.data.success === false) {
                    toast.error(response.data.error, {
                        position: "top-right",
                        autoClose: 3000,
                        hideProgressBar: true,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: false,
                        progress: 0,
                        toastId: "my_toast",
                    });
                } else {
                    toast.success(response.data.message, {
                        position: "top-right",
                        autoClose: 3000,
                        hideProgressBar: true,
                        closeOnClick: true,
                        pauseOnHover: true,
                        draggable: false,
                        progress: 0,
                        toastId: "my_toast",
                    });
                    
                    localStorage.setItem("authorization", response.headers["authorization"]!);
                    setTimeout(() => {
                        navigate("/");
                    }, 1000);
                }
            })
            .catch(function (error) {
                console.log(error);
            });
    };
    return (
        <>
            <div className="App">
                <div
                    className="row d-flex justify-content-center align-items-center"
                    style={{ height: "100vh" }}
                >
                    <div className="card mb-3" style={{ maxWidth: "320px" }}>
                        <div className="col-md-12">
                            <div className="card-body">
                                <h3 className="main_title">
                                    Login Form
                                </h3>
                                <div className="room_form">
                                    <form autoComplete="off" onSubmit={handleSubmit(login)}>
                                        <div className="mb-3 mt-4">
                                            <label className="form-label">Login</label>
                                            <input
                                                type="text"
                                                className="form-control shadow-none"
                                                id="exampleFormControlInput1"
                                                {...register("login", { required: "Login is required!" })}
                                            />
                                            {/* {errors.email && (
                                                <p className="text-danger" style={{ fontSize: 14 }}>
                                                    // @ts-ignore
                                                    {errors.email.message}
                                                </p>
                                            )} */}
                                        </div>
                                        <div className="mb-3">
                                            <label className="form-label">Password</label>
                                            <input
                                                type="password"
                                                className="form-control shadow-none"
                                                id="exampleFormControlInput2"
                                                {...register("password", {
                                                    required: "Password is required!",
                                                })}
                                            />
                                            {/* {errors.password && (
                                                <p className="text-danger" style={{ fontSize: 14 }}>
                                                    // @ts-ignore
                                                    {errors.password.message}
                                                </p>
                                            )} */}
                                        </div>
                                        <div className="text-center mt-4 ">
                                            <button
                                                className="room_btn"
                                                type="submit"
                                            >
                                                Submit
                                            </button>
                                            <p className="card-text pb-2">
                                                Have an Account?{" "}
                                                <Link style={{ textDecoration: "none" }} to={"/register"}>
                                                    Sign Up
                                                </Link>
                                            </p>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <ToastContainer
                position="top-right"
                autoClose={5000}
                hideProgressBar
                closeOnClick
                rtl={false}
                pauseOnFocusLoss={false}
                draggable={false}
                pauseOnHover
                limit={1}
                transition={Flip}
            />
        </>
    );
};
export default Login;
