const BASE_URL = "http://127.0.0.1:8000";

/**
 * Функція логіну (отримання токена)
 */
export const loginUser = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  try {
    const response = await fetch(`${BASE_URL}/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Невірний логін або пароль");
    }

    const data = await response.json();
    return data.access_token;
  } catch (error) {
    console.error("Login Error:", error);
    throw error;
  }
};
