import styles from './ConnectionBadge.module.css'
import { Wifi, WifiOff, Loader } from 'lucide-react'

export function ConnectionBadge({ status }) {
  const config = {
    connected:    { icon: Wifi,    label: 'Connected',    cls: styles.connected },
    connecting:   { icon: Loader,  label: 'Connecting…',  cls: styles.connecting },
    disconnected: { icon: WifiOff, label: 'Disconnected', cls: styles.disconnected },
    error:        { icon: WifiOff, label: 'Error',        cls: styles.error },
  }

  const { icon: Icon, label, cls } = config[status] || config.disconnected
  const isLoading = status === 'connecting'

  return (
    <div className={`${styles.badge} ${cls}`} title={label}>
      <Icon
        size={13}
        className={isLoading ? styles.spin : ''}
      />
      <span>{label}</span>
    </div>
  )
}
