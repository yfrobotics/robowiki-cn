# PID Controller
## Formula

$$ u(t) = K_p e(t) + K_i \int^t_0 e(\tau) d\tau + K_d \frac{de(t)}{dt} $$

The Laplace transform is:
$$ L(s) = U(s)/E(s) = K_p + \frac{K_i}{s} + K_d s $$


## Discretization
A control system is designed in continuous time, however a computer that running the control algorithm needs a digital implementation. Discretization is to convert a system from continuous to discrete time. Typical methods are:

- Forward difference: often for integration part.
- Backward difference: For the derivative part, it is often choose to have a backward difference to have a stable derivative (the result discrete parameters are often position, so no ringing effect).
- Tustin approximation.


---

## Implementation
C code:

```c
  float k_p = 0;
  float k_i = 0;
  float k_d = 0;
  float e_i = 0;  /* integrated error */
  float e_p = 0;  /* previous error */

  void pid_init(float kp_, float ki_, float kd_) {
  	k_p = kp_;
  	k_i = ki_;
  	k_d = kd_;
  	e_i = 0;
  	e_p = 0;
  }

  void pid_controller() {
    float y = adc_input();
    float e = r - y;
    e_i += e * dt;

    float u = k_p * e + k_i * e_i + k_d * (e - e_p) / dt;

    dac_output(u);
    e_p = e;
    sleep(dt);
  }
```
