import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button
from matplotlib.backend_bases import MouseEvent

# Функция строит траекторию сближения, адаптируя курс маневрирующего корабля на каждом шаге
# и рассчитывает минимальное расстояние.
def trajectory_planning(Vm_mag, Vc_mag, P_0, D_0, q_c_0, q_m_0, K, sim_time=100, dt=0.1):

    time = np.arange(0, sim_time, dt)
    n_steps = len(time)

    x_m = 0
    y_m = 0
    x_c = x_m + D_0 * np.cos(P_0)
    y_c = y_m + D_0 * np.sin(P_0)

    traj_m = np.zeros((n_steps, 2))
    traj_c = np.zeros((n_steps, 2))
    traj_m[0] = [x_m, y_m]
    traj_c[0] = [x_c, y_c]

    D = D_0
    tetta = P_0

    D_history = np.zeros(n_steps)
    tetta_history = np.zeros(n_steps)
    q_m_history = np.zeros(n_steps)
    D_history[0] = D
    tetta_history[0] = tetta
    q_m_history[0] = q_m_0

    q_m = q_m_0
    min_distance = D_0
    min_distance_time = 0
    x_m_min_distance = x_m
    y_m_min_distance = y_m
    x_c_min_distance = x_c
    y_c_min_distance = y_c

    close_distance = 10

    for i in range(1, n_steps):
        dD_dt = Vc_mag * np.cos(q_c_0 - tetta) - Vm_mag * np.cos(q_m - tetta)
        dtetta_dt = (Vc_mag * np.sin(q_c_0 - tetta) - Vm_mag * np.sin(q_m - tetta)) / D

        D += dD_dt * dt
        tetta += dtetta_dt * dt

        dqm_dt = K * dtetta_dt
        q_m += dqm_dt * dt

        Vm_x = Vm_mag * np.cos(q_m)
        Vm_y = Vm_mag * np.sin(q_m)
        Vc_x = Vc_mag * np.cos(q_c_0)
        Vc_y = Vc_mag * np.sin(q_c_0)

        x_m += Vm_x * dt
        y_m += Vm_y * dt
        x_c += Vc_x * dt
        y_c += Vc_y * dt

        traj_m[i] = [x_m, y_m]
        traj_c[i] = [x_c, y_c]

        # Update distance and bearing
        D = np.sqrt((x_c - x_m)**2 + (y_c - y_m)**2)
        tetta = np.arctan2(y_c - y_m, x_c - x_m)

        D_history[i] = D
        tetta_history[i] = tetta
        q_m_history[i] = q_m

        # Update minimum distance if needed
        if D < min_distance:
            min_distance = D
            min_distance_time = time[i]
            x_m_min_distance = x_m
            y_m_min_distance = y_m
            x_c_min_distance = x_c
            y_c_min_distance = y_c

        if D <= close_distance:
            traj_m[i:] = traj_m[i-1]
            traj_c[i:] = traj_c[i-1]
            D_history[i:] = D
            tetta_history[i:] = tetta
            q_m_history[i:] = q_m
            break

    return traj_m, traj_c, time[:i+1], D_history[:i+1], tetta_history[:i+1], q_m_history[:i+1], min_distance, min_distance_time, x_m_min_distance, y_m_min_distance, x_c_min_distance, y_c_min_distance

# ِФункция отрисовывает все графики
def visualize_trajectory(ax, traj_m, traj_c, time, Vm_mag, Vc_mag, P_0, D_0, q_c_0, q_m_0, K, D_history, tetta_history, q_m_history, min_distance, min_distance_time, x_m_min_distance, y_m_min_distance, x_c_min_distance, y_c_min_distance):

    x_m0 = traj_m[0, 0]
    y_m0 = traj_m[0, 1]
    x_c0 = traj_c[0, 0]
    y_c0 = traj_c[0, 1]

    x_m_end = traj_m[-1, 0]
    y_m_end = traj_m[-1, 1]
    x_c_end = traj_c[-1, 0]
    y_c_end = traj_c[-1, 1]

    # Clear all axes
    for a in ax.flatten():
        a.clear()

    # --- Top Left: Траектории ---
    ax[0, 0].plot(traj_m[:, 0], traj_m[:, 1], label='Маневрирующий корабль', linewidth=2)
    ax[0, 0].plot(traj_c[:, 0], traj_c[:, 1], label='Корабль-цель', linewidth=2)
    ax[0, 0].plot(x_m0, y_m0, 'o', markersize=10, color='blue', label='Начало (маневрирующий)')
    ax[0, 0].plot(x_c0, y_c0, 'o', markersize=10, color='red', label='Начало (цель)')

    scale = 50
    ax[0, 0].arrow(x_m0, y_m0, Vm_mag * np.cos(q_m_0) * scale, Vm_mag * np.sin(q_m_0) * scale,
             head_width=20, head_length=30, fc='blue', ec='blue', label='Скорость (маневрирующий, начало)')
    ax[0, 0].arrow(x_c0, y_c0, Vc_mag * np.cos(q_c_0) * scale, Vc_mag * np.sin(q_c_0) * scale,
             head_width=20, head_length=30, fc='red', ec='red', label='Скорость (цель)')

    ax[0, 0].plot([x_m0, x_c0], [y_m0, y_c0], '--', color='gray', label='Пеленг')
    arc = patches.Arc((x_m0, y_m0), width=D_0/4, height=D_0/4, angle=0,
                      theta1=0, theta2=np.degrees(P_0), color="green", linestyle=':', label='Угол пеленга')
    ax[0, 0].add_patch(arc)
    ax[0, 0].text(x_m0 + D_0/8 * np.cos(P_0/2), y_m0 + D_0/8 * np.sin(P_0/2), f'{np.degrees(P_0):.1f}°', color='green')
    ax[0, 0].text((x_m0 + x_c0) / 2, (y_m0 + y_c0) / 2, f'{D_0:.0f} м', color='black')

    ax[0, 0].plot([x_m0, x_c_end], [y_m0, y_c_end], linestyle='-', color='green', linewidth=1, label='Линия сближения')

    # Add marker for minimum distance
    ax[0, 0].plot(x_m_min_distance, y_m_min_distance, marker='x', color='purple', markersize=8,
            label=f'Мин. расст.: {min_distance:.1f} м')
    ax[0, 0].plot(x_c_min_distance, y_c_min_distance, marker='x', color='orange', markersize=8)
    ax[0, 0].text((x_m_min_distance + x_c_min_distance)/2, (y_m_min_distance + y_c_min_distance)/2, f't={min_distance_time:.1f}с', color='black')

    ax[0, 0].set_xlabel('x (м)')
    ax[0, 0].set_ylabel('y (м)')
    ax[0, 0].set_title('Траектории сближения кораблей')
    ax[0, 0].legend(loc='upper left')
    ax[0, 0].grid(True)
    ax[0, 0].axis('equal')

    # Top Right: Расстояние от времени
    ax[0, 1].plot(time, D_history, label='Дистанция')
    ax[0, 1].set_xlabel('Время (с)')
    ax[0, 1].set_ylabel('Расстояние (м)')
    ax[0, 1].set_title('Изменение дистанции со временем')
    ax[0, 1].grid(True)

    # Bottom Right: Пеленг от времени
    ax[1, 0].plot(time, tetta_history, label='Пеленг')
    ax[1, 0].set_xlabel('Время (с)')
    ax[1, 0].set_ylabel('Пеленг (рад)')
    ax[1, 0].set_title('Изменение пеленга со временем')
    ax[1, 0].grid(True)

    # Bottom Right: Курс от времени
    ax[1, 1].plot(time, q_m_history, label='Курс', color='purple')
    ax[1, 1].set_xlabel('Время (с)')
    ax[1, 1].set_ylabel('Курс (рад)')
    ax[1, 1].set_title('Изменение курса маневрирующего корабля со временем')
    ax[1, 1].grid(True)

    fig.canvas.draw_idle()

# Функция изменения масштаба основного графика
def zoom_callback(event):
    if event.inaxes == axes[0, 0]:  # Check if the event is in the desired axes
        base_scale = 1.2  # Zoom scale factor
        cur_xlim = axes[0, 0].get_xlim()
        cur_ylim = axes[0, 0].get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata  # Get the mouse position
        ydata = event.ydata

        if event.button == 'up':
            # Zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # Zoom out
            scale_factor = base_scale
        else:
            scale_factor = 1

        new_xlim = (xdata - cur_xrange * scale_factor,
                    xdata + cur_xrange * scale_factor)
        new_ylim = (ydata - cur_yrange * scale_factor,
                    ydata + cur_yrange * scale_factor)

        axes[0, 0].set_xlim(new_xlim)
        axes[0, 0].set_ylim(new_ylim)

        fig.canvas.draw_idle()  # Redraw the canvas

# Функция для обновления графиков при изменении значений слайдеров
def update(val):

    Vm_mag = slider_Vm.val
    Vc_mag = slider_Vc.val
    P_0 = slider_P0.val
    D_0 = slider_D0.val
    q_c_0 = slider_qc0.val
    q_m_0 = slider_qm0.val
    K = slider_K.val

    traj_m, traj_c, time, D_history, tetta_history, q_m_history, min_distance, min_distance_time, x_m_min_distance, y_m_min_distance, x_c_min_distance, y_c_min_distance = trajectory_planning(Vm_mag, Vc_mag, P_0, D_0, q_c_0, q_m_0, K, sim_time, dt)

    visualize_trajectory(axes, traj_m, traj_c, time, Vm_mag, Vc_mag, P_0, D_0, q_c_0, q_m_0, K, D_history, tetta_history, q_m_history, min_distance, min_distance_time, x_m_min_distance, y_m_min_distance, x_c_min_distance, y_c_min_distance)


# Main
if __name__ == '__main__':
    # Initial conditions
    Vm_mag_initial = 5
    Vc_mag_initial = 3
    P_0_initial = np.pi - np.pi / 10
    D_0_initial = 1000
    q_c_0_initial = 0
    q_m_0_initial = np.pi / 2 + np.pi / 6
    K_initial = 1.0

    # Simulation parameters
    sim_time = 500
    dt = 0.1

    # Create figure and axes with custom layout
    fig, axes = plt.subplots(2, 2, figsize=(18, 9))  # Adjusted figure size

    # Define positions for the plots
    trajectory_plot_pos = [0.05, 0.25, 0.65, 0.7]  # Main plot - take 65% of the width, 70% of height
    distance_plot_pos = [0.75, 0.75, 0.2, 0.15] # Right-side plots take 20% of width each, 20% of height each
    bearing_plot_pos = [0.75, 0.50, 0.2, 0.15]
    course_plot_pos = [0.75, 0.25, 0.2, 0.15]

    axes[0, 0].set_position(trajectory_plot_pos) # Main trajectory plot

    # The other three plots are placed on the right side
    axes[0, 1].set_position(distance_plot_pos)
    axes[1, 0].set_position(bearing_plot_pos)
    axes[1, 1].set_position(course_plot_pos)

    # Slider definitions (smaller and at the bottom, arranged in two rows)
    slider_width, slider_height = 0.1, 0.02 # width = 12%, height = 2%
    slider_bottom1 = 0.07 # 1st row of sliders
    slider_bottom2 = 0.01 # 2nd row of sliders

    # First row
    ax_Vm = plt.axes([0.05, slider_bottom1, slider_width, slider_height])
    ax_Vc = plt.axes([0.35, slider_bottom1, slider_width, slider_height])
    ax_P0 = plt.axes([0.65, slider_bottom1, slider_width, slider_height])

    # Second row
    ax_D0 = plt.axes([0.05, slider_bottom2, slider_width, slider_height])
    ax_qc0 = plt.axes([0.25, slider_bottom2, slider_width, slider_height])
    ax_qm0 = plt.axes([0.45, slider_bottom2, slider_width, slider_height])
    ax_K = plt.axes([0.65, slider_bottom2, slider_width, slider_height])

    # Sliders
    slider_Vm = Slider(ax_Vm, 'Vm', 1, 10, valinit=Vm_mag_initial)
    slider_Vc = Slider(ax_Vc, 'Vc', 1, 10, valinit=Vc_mag_initial)
    slider_P0 = Slider(ax_P0, 'P0 (rad)', 0, np.pi, valinit=P_0_initial)
    slider_D0 = Slider(ax_D0, 'D0', 500, 4000, valinit=D_0_initial)
    slider_qc0 = Slider(ax_qc0, 'qc0 (rad)', -np.pi, np.pi, valinit=q_c_0_initial)
    slider_qm0 = Slider(ax_qm0, 'qm0 (rad)', -np.pi, np.pi, valinit=q_m_0_initial)
    slider_K = Slider(ax_K, 'K', 0.1, 30, valinit=K_initial)

    # Attach the zoom callback
    fig.canvas.mpl_connect('scroll_event', zoom_callback)

    # Call update function when slider value changes
    slider_Vm.on_changed(update)
    slider_Vc.on_changed(update)
    slider_P0.on_changed(update)
    slider_D0.on_changed(update)
    slider_qc0.on_changed(update)
    slider_qm0.on_changed(update)
    slider_K.on_changed(update)

    # Initial plot
    traj_m, traj_c, time, D_history, tetta_history, q_m_history, min_distance, min_distance_time, x_m_min_distance, y_m_min_distance, x_c_min_distance, y_c_min_distance = trajectory_planning(Vm_mag_initial, Vc_mag_initial, P_0_initial, D_0_initial, q_c_0_initial, q_m_0_initial, K_initial, sim_time, dt)

    visualize_trajectory(axes, traj_m, traj_c, time, Vm_mag_initial, Vc_mag_initial, P_0_initial, D_0_initial, q_c_0_initial, q_m_0_initial, K_initial, D_history, tetta_history, q_m_history, min_distance, min_distance_time, x_m_min_distance, y_m_min_distance, x_c_min_distance, y_c_min_distance)

    plt.show()